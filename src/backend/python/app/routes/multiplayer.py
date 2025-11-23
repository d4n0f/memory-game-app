from flask import Blueprint, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from ..models.database import get_db_connect
from ..models.user import get_or_create_player
from .auth import get_current_user
from ..utils.logger import get_logger, setup_logger
import random
import string
import time
from datetime import datetime
import threading

multiplayer_bp = Blueprint('multiplayer', __name__)
# Logger inicializálása console és file handler-rel
logger = setup_logger('multiplayer')

# SocketIO instance (app/__init__.py-ban kell inicializálni)
socketio = None

def get_socketio():
    """SocketIO instance lekérése"""
    return socketio

# Aktív szobák memóriában (in-memory state)
active_rooms = {}  # {room_code: RoomState}

# Color-hunter képek listája
COLOR_HUNTER_IMAGES = [
    "../../assets/images/color-hunter/kep1.jpg",
    "../../assets/images/color-hunter/kep2.jpg",
    "../../assets/images/color-hunter/kep3.jpg",
    "../../assets/images/color-hunter/kep4.jpg",
    "../../assets/images/color-hunter/kep5.jpg",
    "../../assets/images/color-hunter/kep6.jpg",
    "../../assets/images/color-hunter/kep7.jpg",
    "../../assets/images/color-hunter/kep8.jpg",
    "../../assets/images/color-hunter/kep9.jpg",
    "../../assets/images/color-hunter/kep10.jpg",
    "../../assets/images/color-hunter/kep11.jpg",
    "../../assets/images/color-hunter/kep12.jpg",
    "../../assets/images/color-hunter/kep13.jpg",
    "../../assets/images/color-hunter/kep14.jpg"
]


class RoomState:
    #Szoba állapot osztály
    def __init__(self, room_code, host_id, max_players=6):
        self.room_code = room_code
        # JAVÍTÁS: host_id biztosan integerre konvertálása
        self.host_id = int(host_id) if host_id is not None else None
        self.max_players = max_players
        self.players = {}  # {player_id: {'name': str, 'socket_id': str, 'score': int, 'active': bool}}
        self.status = 'waiting'  # waiting, playing, finished
        self.current_round = 0
        self.current_target_image = None
        self.round_start_time = None
        self.round_responses = {}  # {player_id: {'choice': str, 'time_ms': int, 'correct': bool}}
        self.round_finished = False
        self.round_timer_thread = None
        self.expected_respondents = set()  # player_ids expected to answer this round (snapshot at round start)


def generate_room_code():
    #6 karakteres belépési kód generálása
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


def init_socketio(app_instance):
    #SocketIO inicializálása és event handler-ek regisztrálása
    global socketio
    # Eventlet használata, ha elérhető, különben threading
    try:
        import eventlet
        socketio = SocketIO(app_instance, cors_allowed_origins="*", async_mode='eventlet')
    except ImportError:
        socketio = SocketIO(app_instance, cors_allowed_origins="*", async_mode='threading')
    
    # Event handler-ek regisztrálása
    socketio.on_event('connect', handle_connect)
    socketio.on_event('disconnect', handle_disconnect)
    socketio.on_event('join_room', handle_join_room)
    socketio.on_event('start_game', handle_start_game)
    socketio.on_event('player_answer', handle_player_answer)
    
    return socketio


@multiplayer_bp.route('/api/multiplayer/create-room', methods=['POST'])
def create_room():
    #Szoba létrehozása
    try:
        # JAVÍTÁS: player_id-t a request body-ból olvassuk, nem a session-ből
        # Ez lehetővé teszi, hogy különböző ablakokban különböző felhasználók legyenek
        data = request.get_json() or {}
        player_id_from_request = data.get('player_id')
        
        # Ha van a request-ben, akkor azt használjuk
        if player_id_from_request:
            player_id = int(player_id_from_request)
            # Username-t lekérjük az adatbázisból
            username = 'Guest'
            conn = get_db_connect()
            if conn:
                cursor = conn.cursor(dictionary=True)
                # Először próbáljuk a players táblából a display_name-t
                cursor.execute('SELECT display_name, user_id FROM players WHERE id = %s', (player_id,))
                player_row = cursor.fetchone()
                if player_row:
                    username = player_row['display_name'] or 'Guest'
                    # Ha van user_id, akkor próbáljuk a username-t is
                    if player_row['user_id']:
                        cursor.execute('SELECT username FROM users WHERE id = %s', (player_row['user_id'],))
                        user_row = cursor.fetchone()
                        if user_row and user_row['username']:
                            username = user_row['username']
                cursor.close()
                conn.close()
        else:
            # Fallback: ha nincs a request-ben, akkor próbáljuk a session-ből (backward compatibility)
            current_user = get_current_user()
            if not current_user:
                return jsonify({'success': False, 'error': 'Nincs bejelentkezve'}), 401
            player_id = current_user.get('player_id')
            username = current_user.get('username', 'Guest')
            if player_id:
                player_id = int(player_id)
        
        if not player_id:
            return jsonify({'success': False, 'error': 'Nincs player_id'}), 400
        
        # Szoba kód generálása (egyediség ellenőrzéssel)
        conn = get_db_connect()
        if not conn:
            return jsonify({'success': False, 'error': 'Adatbázis hiba'}), 500
        
        cursor = conn.cursor()
        room_code = None
        for _ in range(10):  # Maximum 10 próbálkozás
            candidate_code = generate_room_code()
            cursor.execute('SELECT id FROM multiplayer_rooms WHERE room_code = %s', (candidate_code,))
            if not cursor.fetchone():
                room_code = candidate_code
                break
        
        if not room_code:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'error': 'Nem sikerült egyedi kódot generálni'}), 500
        
        # Adatbázisba mentés
        cursor.execute('''
            INSERT INTO multiplayer_rooms (room_code, host_player_id, status)
            VALUES (%s, %s, 'waiting')
        ''', (room_code, player_id))
        room_id = cursor.lastrowid
        
        # Host hozzáadása room_players táblához
        cursor.execute('''
            INSERT INTO room_players (room_id, player_id)
            VALUES (%s, %s)
        ''', (room_id, player_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # In-memory state létrehozása
        # player_id már integer (a fenti kódban konvertálva)
        active_rooms[room_code] = RoomState(room_code, player_id)
        active_rooms[room_code].players[player_id] = {
            'name': username,
            'socket_id': None,
            'score': 0,
            'active': True
        }
        
        logger.info(f"Szoba létrehozva | room_code: {room_code} | host_id: {player_id} | username: {username} | player_id_from_request: {player_id_from_request}")
        
        return jsonify({
            'success': True,
            'room_code': room_code,
            'room_id': room_id,
            'host_id': player_id  # JAVÍTÁS: host_id visszaadása a frontend-nek
        })
    except Exception as e:
        logger.error(f"Szoba létrehozási hiba: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@multiplayer_bp.route('/api/multiplayer/join-room/<room_code>', methods=['POST'])
def join_room_api(room_code):
    #Szobához csatlakozás API
    try:
        # JAVÍTÁS: player_id-t a request body-ból olvassuk, nem a session-ből
        # Ez lehetővé teszi, hogy különböző ablakokban különböző felhasználók legyenek
        data = request.get_json() or {}
        player_id_from_request = data.get('player_id')
        
        # Ha van a request-ben, akkor azt használjuk
        if player_id_from_request:
            player_id = int(player_id_from_request)
            # Username-t lekérjük az adatbázisból
            username = 'Guest'
            conn = get_db_connect()
            if conn:
                cursor = conn.cursor(dictionary=True)
                # Először próbáljuk a players táblából a display_name-t
                cursor.execute('SELECT display_name, user_id FROM players WHERE id = %s', (player_id,))
                player_row = cursor.fetchone()
                if player_row:
                    username = player_row['display_name'] or 'Guest'
                    # Ha van user_id, akkor próbáljuk a username-t is
                    if player_row['user_id']:
                        cursor.execute('SELECT username FROM users WHERE id = %s', (player_row['user_id'],))
                        user_row = cursor.fetchone()
                        if user_row and user_row['username']:
                            username = user_row['username']
                cursor.close()
                conn.close()
        else:
            # Fallback: ha nincs a request-ben, akkor próbáljuk a session-ből (backward compatibility)
            current_user = get_current_user()
            if not current_user:
                return jsonify({'success': False, 'error': 'Nincs bejelentkezve'}), 401
            player_id = current_user.get('player_id')
            username = current_user.get('username', 'Guest')
            if player_id:
                player_id = int(player_id)
        
        if not player_id:
            return jsonify({'success': False, 'error': 'Nincs player_id'}), 400
        
        # Szoba ellenőrzése
        conn = get_db_connect()
        if not conn:
            return jsonify({'success': False, 'error': 'Adatbázis hiba'}), 500
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT id, host_player_id, status, max_players
            FROM multiplayer_rooms
            WHERE room_code = %s
        ''', (room_code,))
        room = cursor.fetchone()
        
        if not room:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'error': 'Szoba nem található'}), 404
        
        # Aktív játékosok száma
        cursor.execute('''
            SELECT COUNT(*) as count
            FROM room_players
            WHERE room_id = %s AND is_active = TRUE
        ''', (room['id'],))
        player_count = cursor.fetchone()['count']
        
        if player_count >= room['max_players']:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'error': 'A szoba tele van'}), 400
        
        if room['status'] != 'waiting':
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'error': 'A játék már elkezdődött'}), 400
        
        # Játékos hozzáadása
        cursor.execute('''
            INSERT INTO room_players (room_id, player_id)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE is_active = TRUE
        ''', (room['id'], player_id))
        conn.commit()
        cursor.close()
        conn.close()
        
        # In-memory state frissítése
        if room_code not in active_rooms:
            host_player_id = int(room['host_player_id'])
            active_rooms[room_code] = RoomState(room_code, host_player_id)
        
        # player_id már integer (a fenti kódban konvertálva)
        active_rooms[room_code].players[player_id] = {
            'name': username,
            'socket_id': None,
            'score': 0,
            'active': True
        }
        
        logger.info(f"Játékos csatlakozott | room_code: {room_code} | player_id: {player_id}")
        
        return jsonify({
            'success': True,
            'room_id': room['id'],
            'is_host': room['host_player_id'] == player_id,
            'host_id': room['host_player_id']  # JAVÍTÁS: host_id visszaadása a frontend-nek
        })
    except Exception as e:
        logger.error(f"Szobához csatlakozási hiba: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@multiplayer_bp.route('/api/multiplayer/room-info/<room_code>', methods=['GET'])
def get_room_info(room_code):
    #Szoba információk lekérése
    try:
        conn = get_db_connect()
        if not conn:
            return jsonify({'success': False, 'error': 'Adatbázis hiba'}), 500
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT mr.*, COUNT(rp.id) as player_count
            FROM multiplayer_rooms mr
            LEFT JOIN room_players rp ON mr.id = rp.room_id AND rp.is_active = TRUE
            WHERE mr.room_code = %s
            GROUP BY mr.id
        ''', (room_code,))
        room = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not room:
            return jsonify({'success': False, 'error': 'Szoba nem található'}), 404
        
        return jsonify({
            'success': True,
            'room': {
                'room_code': room['room_code'],
                'status': room['status'],
                'player_count': room['player_count'],
                'max_players': room['max_players']
            }
        })
    except Exception as e:
        logger.error(f"Szoba info lekérési hiba: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


# WebSocket esemény handler függvények (lazy registration)

def handle_connect():
    #WebSocket kapcsolat létrejött
    logger.info(f"WebSocket kapcsolat: {request.sid}")


def handle_disconnect():
    #WebSocket kapcsolat megszakadt
    logger.info(f"WebSocket kapcsolat megszakadt: {request.sid}")
    # Játékos eltávolítása a szobákból
    for room_code, room_state in list(active_rooms.items()):
        for player_id, player_data in list(room_state.players.items()):
            if player_data.get('socket_id') == request.sid:
                leave_room(room_code)
                del room_state.players[player_id]
                socketio.emit('player_left', {
                    'player_id': player_id,
                    'player_name': player_data['name']
                }, room=room_code)
                # Ha üres a szoba, töröljük
                if not room_state.players:
                    del active_rooms[room_code]
                break


def handle_join_room(data):
    #Játékos csatlakozik a szobához WebSocket-en keresztül
    try:
        room_code = data.get('room_code')
        player_id = data.get('player_id')
        
        if not room_code or not player_id:
            emit('error', {'message': 'Hiányzó adatok'})
            return
        
        if room_code not in active_rooms:
            emit('error', {'message': 'Szoba nem található'})
            return
        
        room_state = active_rooms[room_code]
        player_id = int(player_id)
        
        if player_id not in room_state.players:
            emit('error', {'message': 'Nem vagy tagja ennek a szobának'})
            return
        
        # Socket ID beállítása
        room_state.players[player_id]['socket_id'] = request.sid
        join_room(room_code)
        
        # Játékosok listájának küldése
        players_list = [
            {
                'player_id': pid,
                'name': pdata['name'],
                'score': pdata['score'],
                'is_host': pid == room_state.host_id
            }
            for pid, pdata in room_state.players.items()
        ]
        
        emit('room_joined', {
            'room_code': room_code,
            'players': players_list,
            'is_host': player_id == room_state.host_id,
            'status': room_state.status,
            'host_id': room_state.host_id  # JAVÍTÁS: host_id küldése a frontend-nek
        })
        
        # Mindenki másnak értesítés
        socketio.emit('player_joined', {
            'player_id': player_id,
            'player_name': room_state.players[player_id]['name'],
            'players': players_list
        }, room=room_code, include_self=False)
        
        logger.info(f"Játékos WebSocket-en csatlakozott | room_code: {room_code} | player_id: {player_id}")
        
    except Exception as e:
        logger.error(f"Join room hiba: {e}", exc_info=True)
        emit('error', {'message': str(e)})


def handle_start_game(data):
    #Host indítja a játékot
    try:
        room_code = data.get('room_code')
        player_id = data.get('player_id')
        
        if not room_code or not player_id:
            emit('error', {'message': 'Hiányzó adatok'})
            return
        
        if room_code not in active_rooms:
            emit('error', {'message': 'Szoba nem található'})
            return
        
        room_state = active_rooms[room_code]
        player_id = int(player_id)
        
        # JAVÍTÁS: host_id biztosan integerre konvertálása
        if room_state.host_id is None:
            logger.error(f"Start game hiba: host_id None | room_code: {room_code}")
            emit('error', {'message': 'Szoba host_id hiányzik'})
            return
        
        host_id = int(room_state.host_id)

        logger.info(f"Start game ellenőrzés | room_code: {room_code} | player_id: {player_id} (type: {type(player_id).__name__}) | host_id: {host_id} (type: {type(host_id).__name__}) | egyezik: {player_id == host_id}")
        
        # Csak a host indíthatja
        if player_id != host_id:
            logger.warning(
                f"Start game elutasítva | room_code: {room_code} | player_id: {player_id} | host_id: {host_id} | player_id type: {type(player_id).__name__} | host_id type: {type(host_id).__name__}")
            emit('error', {'message': 'Csak a host indíthatja a játékot'})
            return
        
        # Legalább 2 játékos kell
        if len(room_state.players) < 2:
            emit('error', {'message': 'Legalább 2 játékos szükséges'})
            return
        
        # Szoba státusz frissítése
        room_state.status = 'playing'
        room_state.current_round = 1
        # Adatbázis frissítése
        conn = get_db_connect()
        if conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE multiplayer_rooms
                SET status = 'playing', started_at = %s
                WHERE room_code = %s
            ''', (datetime.now(), room_code))
            conn.commit()
            cursor.close()
            conn.close()
        
        # Első kör indítása
        start_round(room_code)
        
        logger.info(f"Játék indítva | room_code: {room_code}")
        
    except Exception as e:
        logger.error(f"Start game hiba: {e}", exc_info=True)
        emit('error', {'message': str(e)})


def start_round(room_code):
    #Kör indítása
    if room_code not in active_rooms:
        return
    
    room_state = active_rooms[room_code]
    
    # Aktív játékosok száma
    active_count = sum(1 for p in room_state.players.values() if p['active'])
    
    # Kép választása
    target_image = random.choice(COLOR_HUNTER_IMAGES)
    room_state.current_target_image = target_image
    room_state.round_responses = {}
    room_state.round_finished = False
    # Snapshot expected respondents at the start of the round
    room_state.expected_respondents = set(
        [pid for pid, pdata in room_state.players.items() if pdata.get('active')]
    )
    room_state.round_start_time = time.time()
    
    # Választási lehetőségek generálása
    shuffled = COLOR_HUNTER_IMAGES.copy()
    random.shuffle(shuffled)
    options = [target_image] + [img for img in shuffled if img != target_image][:3]
    random.shuffle(options)
    
    logger.info(f"Kör indítva | room_code: {room_code} | round: {room_state.current_round} | aktív játékosok: {active_count}")
    
    # Minden aktív játékosnak küldjük
    socketio.emit('round_start', {
        'round_number': room_state.current_round,
        'target_image': target_image,
        'options': options,
        'view_time': 5  # Másodperc, amíg látható a kép
    }, room=room_code)
    
    # Timer: 5 másodperc után választási fázis
    def timer_callback():
        time.sleep(5)
        if room_code in active_rooms and not active_rooms[room_code].round_finished:
            logger.debug(f"Választási fázis kezdődik | room_code: {room_code} | round: {active_rooms[room_code].current_round}")
            socketio.emit('show_choices', {
                'round_number': active_rooms[room_code].current_round
            }, room=room_code)
            
            # Válaszadási idő: 10 másodperc
            time.sleep(10)
            
            # Kör vége (idő lejárt)
            if room_code in active_rooms and not active_rooms[room_code].round_finished:
                logger.debug(f"Válaszadási idő lejárt | room_code: {room_code} | round: {active_rooms[room_code].current_round}")
                end_round(room_code)
    
    room_state.round_timer_thread = threading.Thread(target=timer_callback, daemon=True)
    room_state.round_timer_thread.start()


def handle_player_answer(data):
    #Játékos válasza
    try:
        room_code = data.get('room_code')
        player_id = data.get('player_id')
        choice = data.get('choice')
        
        if not room_code or not player_id or not choice:
            return
        
        if room_code not in active_rooms:
            return
        
        room_state = active_rooms[room_code]
        player_id = int(player_id)
        
        # Már válaszolt?
        if player_id in room_state.round_responses:
            return
        
        # Nincs aktív kör?
        if room_state.round_finished or room_state.status != 'playing':
            return
        
        # Válaszidő számítása
        response_time = (time.time() - room_state.round_start_time) * 1000  # ms
        
        # Helyesség ellenőrzése
        is_correct = (choice == room_state.current_target_image)
        
        # Válasz mentése
        room_state.round_responses[player_id] = {
            'choice': choice,
            'time_ms': int(response_time),
            'correct': is_correct
        }
        
        player_name = room_state.players[player_id]['name']
        logger.debug(f"Játékos válasz | room_code: {room_code} | round: {room_state.current_round} | player_id: {player_id} | player_name: {player_name} | helyes: {is_correct} | idő: {int(response_time)}ms")
        
        # Ha hibázott, kiesik (last man standing)
        if not is_correct:
            room_state.players[player_id]['active'] = False
            logger.info(f"Játékos kiesett hibás válasz miatt | room_code: {room_code} | round: {room_state.current_round} | player_id: {player_id} | player_name: {player_name}")
            # Adatbázis frissítése
            conn = get_db_connect()
            if conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE room_players
                    SET is_active = FALSE
                    WHERE room_id = (SELECT id FROM multiplayer_rooms WHERE room_code = %s)
                    AND player_id = %s
                ''', (room_code, player_id))
                conn.commit()
                cursor.close()
                conn.close()
        
        # Mindenki válaszolt? -> use snapshot of expected respondents
        expected = set(pid for pid in room_state.expected_respondents if pid in room_state.players)
        if not expected:
            # fallback: current active players
            expected = set(pid for pid, pdata in room_state.players.items() if pdata.get('active'))

        if len(room_state.round_responses) >= len(expected):
            # Mindenki válaszolt, azonnal vége a körnek
            logger.debug(f"Minden játékos válaszolt, kör vége | room_code: {room_code} | round: {room_state.current_round} | válaszok: {len(room_state.round_responses)} | expected: {len(expected)}")
            end_round(room_code)
        
    except Exception as e:
        logger.error(f"Player answer hiba: {e}", exc_info=True)


def end_round(room_code):
    #Kör vége
    if room_code not in active_rooms:
        return
    
    room_state = active_rooms[room_code]
    
    if room_state.round_finished:
        return
    
    room_state.round_finished = True
    # Clear expected respondents snapshot for this round
    room_state.expected_respondents = set()
    
    # Aktív játékosok (akik helyesen válaszoltak)
    active_responses = {
        pid: resp for pid, resp in room_state.round_responses.items()
        if resp['correct'] and room_state.players[pid]['active']
    }
    
    # MINDEN körben gyorsaság alapján rendezzük (1. körben is)
    sorted_players = sorted(
        active_responses.items(),
        key=lambda x: x[1]['time_ms']
    )
    
    # JAVÍTÁS: Ha 4 vagy több játékos helyesen válaszolt, akkor a leglassabb kiesik
    # (Ha 3 vagy kevesebb van, akkor mindenki kap pontot: 1. = 3, 2. = 2, 3. = 1)
    if len(sorted_players) > 3:
        # A leglassabb játékos kiesik
        slowest_player_id = sorted_players[-1][0]
        room_state.players[slowest_player_id]['active'] = False
        
        # Adatbázis frissítése
        conn_kick = get_db_connect()
        if conn_kick:
            cursor_kick = conn_kick.cursor()
            try:
                cursor_kick.execute('''
                    UPDATE room_players
                    SET is_active = FALSE
                    WHERE room_id = (SELECT id FROM multiplayer_rooms WHERE room_code = %s)
                    AND player_id = %s
                ''', (room_code, slowest_player_id))
                conn_kick.commit()
            except Exception as e:
                logger.error(f"Player kiesés adatbázis hiba: {e}", exc_info=True)
            finally:
                cursor_kick.close()
                conn_kick.close()
        
        slowest_player_name = room_state.players[slowest_player_id]['name']
        logger.info(f"Játékos kiesett gyorsaság alapján | room_code: {room_code} | round: {room_state.current_round} | player_id: {slowest_player_id} | player_name: {slowest_player_name}")
        
        # A kiesett játékost eltávolítjuk a sorted_players-ből, hogy ne kapjon pontot
        sorted_players = sorted_players[:-1]
    
    # Pontok osztása (csak az első 3 helyezett kap pontot)
    points_map = {1: 3, 2: 2, 3: 1}  # 1. = 3, 2. = 2, 3. = 1
    
    round_results = []
    conn = get_db_connect()
    cursor = None
    
    points_summary = []
    
    # JAVÍTÁS: Egyetlen cursor használata, commit a ciklus után
    if conn:
        try:
            cursor = conn.cursor()
            
            for position, (player_id, response) in enumerate(sorted_players[:3], 1):
                points = points_map.get(position, 0)
                room_state.players[player_id]['score'] += points
                player_name = room_state.players[player_id]['name']
                
                points_summary.append(f"{position}. {player_name} (+{points} pont, {response['time_ms']}ms)")
                
                round_results.append({
                    'player_id': player_id,
                    'player_name': player_name,
                    'position': position,
                    'points': points,
                    'time_ms': response['time_ms']
                })
                
                # Adatbázisba mentés
                cursor.execute('''
                    INSERT INTO round_results 
                    (room_id, round_number, player_id, is_correct, response_time_ms, points_earned, position_in_round)
                    VALUES (
                        (SELECT id FROM multiplayer_rooms WHERE room_code = %s),
                        %s, %s, %s, %s, %s, %s
                    )
                ''', (room_code, room_state.current_round, player_id, True, response['time_ms'], points, position))
                
                # room_players total_score frissítése
                cursor.execute('''
                    UPDATE room_players
                    SET total_score = %s
                    WHERE room_id = (SELECT id FROM multiplayer_rooms WHERE room_code = %s)
                    AND player_id = %s
                ''', (room_state.players[player_id]['score'], room_code, player_id))
            
            # Commit csak akkor, ha minden sikeres volt
            conn.commit()
            logger.debug(f"Round results mentve | room_code: {room_code} | round: {room_state.current_round} | {len(round_results)} eredmény")
        except Exception as e:
            logger.error(f"Round result mentési hiba: {e}", exc_info=True)
            if conn:
                conn.rollback()
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    # Aktív játékosok száma
    active_count = sum(1 for p in room_state.players.values() if p['active'])
    
    # Kör vége logolás
    logger.info(f"Kör vége | room_code: {room_code} | round: {room_state.current_round} | aktív játékosok: {active_count} | pontok: {'; '.join(points_summary) if points_summary else 'nincs'}")
    
    # Eredmények küldése
    # Prepare per-player response summary to send to clients
    response_summary = {
        pid: {
            'choice': resp.get('choice'),
            'time_ms': resp.get('time_ms'),
            'correct': resp.get('correct', False)
        }
        for pid, resp in room_state.round_responses.items()
    }

    socketio.emit('round_end', {
        'round_number': room_state.current_round,
        'results': round_results,
        'leaderboard': get_leaderboard(room_state),
        'round_responses': response_summary
    }, room=room_code)
    
    if active_count <= 1:
        # Játék vége
        end_game(room_code)
    else:
        # Következő kör késleltetése
        def next_round_delay():
            time.sleep(5)
            if room_code in active_rooms:
                room_state.current_round += 1
                start_round(room_code)
        
        threading.Thread(target=next_round_delay, daemon=True).start()


def get_leaderboard(room_state):
    #Ranglista generálása
    players_list = [
        {
            'player_id': pid,
            'name': pdata['name'],
            'score': pdata['score'],
            'active': pdata['active']
        }
        for pid, pdata in room_state.players.items()
    ]
    return sorted(players_list, key=lambda x: x['score'], reverse=True)


def end_game(room_code):
    #Játék vége
    if room_code not in active_rooms:
        return
    
    room_state = active_rooms[room_code]
    room_state.status = 'finished'
    
    # Végső ranglista
    final_leaderboard = get_leaderboard(room_state)
    
    # Adatbázis frissítése
    conn = get_db_connect()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE multiplayer_rooms
                SET status = 'finished', finished_at = %s
                WHERE room_code = %s
            ''', (datetime.now(), room_code))
            
            # Játékosok pozícióinak mentése
            for position, player_data in enumerate(final_leaderboard, 1):
                cursor.execute('''
                    UPDATE room_players
                    SET position = %s, total_score = %s
                    WHERE room_id = (SELECT id FROM multiplayer_rooms WHERE room_code = %s)
                    AND player_id = %s
                ''', (position, player_data['score'], room_code, player_data['player_id']))
            
            conn.commit()
        except Exception as e:
            logger.error(f"Game end adatbázis hiba: {e}", exc_info=True)
        finally:
            cursor.close()
            conn.close()
    
    # Eredmények küldése
    socketio.emit('game_end', {
        'leaderboard': final_leaderboard
    }, room=room_code)
    
    logger.info(f"Játék vége | room_code: {room_code}")
    
    # Szoba törlése in-memory-ből 30 másodperc után
    def cleanup_room_memory():
        time.sleep(30)
        if room_code in active_rooms:
            del active_rooms[room_code]
            logger.debug(f"Szoba törölve in-memory-ből | room_code: {room_code}")
    
    threading.Thread(target=cleanup_room_memory, daemon=True).start()
    
    # Szoba törlése adatbázisból 1 óra után
    def cleanup_room_database():
        time.sleep(3600)  # 1 óra = 3600 másodperc
        conn = get_db_connect()
        if conn:
            cursor = conn.cursor()
            try:
                # Először lekérjük a room_id-t
                cursor.execute('SELECT id FROM multiplayer_rooms WHERE room_code = %s', (room_code,))
                room_result = cursor.fetchone()
                
                if room_result:
                    room_id = room_result[0]
                    
                    # Törlés: round_results -> room_players -> multiplayer_rooms
                    # (A foreign key cascade-ek automatikusan törlik a kapcsolódó rekordokat)
                    cursor.execute('DELETE FROM multiplayer_rooms WHERE room_code = %s', (room_code,))
                    conn.commit()
                    
                    logger.info(f"Szoba törölve adatbázisból | room_code: {room_code} | room_id: {room_id}")
                else:
                    logger.debug(f"Szoba már törölve volt az adatbázisból | room_code: {room_code}")
            except Exception as e:
                logger.error(f"Szoba törlési hiba adatbázisból: {e} | room_code: {room_code}", exc_info=True)
                if conn.is_connected():
                    conn.rollback()
            finally:
                cursor.close()
                conn.close()
    
    threading.Thread(target=cleanup_room_database, daemon=True).start()


@multiplayer_bp.route('/color-hunter/wrong-answer')
def multiplayer_wrong():
    return render_template('game/color-hunter/color-hunter-result-wrong.html')

@multiplayer_bp.route('/color-hunter/correct-answer')
def multiplayer_correct():
    return render_template('game/color-hunter/color-hunter-result-correct.html')