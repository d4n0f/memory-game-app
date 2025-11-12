from flask import request, jsonify, session, redirect, url_for, render_template, Blueprint
from ..models.user import get_or_create_player
from ..models.database import get_db_connect
from .auth import get_current_user
from datetime import datetime
import mysql.connector
from ..utils.logger import get_logger

game_bp = Blueprint('game', __name__)
logger = get_logger('game')


@game_bp.route('/start-game', methods=['POST'])
def start_game():
    #Játék indítása a főoldalról
    try:
        player_name = request.form.get('player_name', '').strip()
        ip_address = request.remote_addr

        if not player_name:
            logger.warning(f"Játék indítási kísérlet név nélkül | IP: {ip_address}")
            return redirect(url_for('index', error='Nincs név megadva'))

        if not (1 <= len(player_name) <= 50):
            logger.warning(f"Játék indítási kísérlet érvénytelen névvel | player_name: {player_name} | IP: {ip_address}")
            return redirect(url_for('index', error='A név hossza 1–30 karakter között lehet.'))

        # Ha be van jelentkezve, akkor a user adataival, különben vendégként
        current_user = get_current_user()
        user_id = current_user['user_id'] if current_user else None

        player_id = get_or_create_player(player_name, user_id)

        if not player_id:
            logger.error(f"Játékos létrehozási hiba játék indításakor | player_name: {player_name} | user_id: {user_id} | IP: {ip_address}")
            return redirect(url_for('index', error='Hiba a játékos létrehozásakor'))

        session['player_name'] = player_name
        session['player_id'] = player_id

        # Game session létrehozása
        game_session_id = create_game_session(player_id, 'color-hunter', 'easy')
        session['game_session_id'] = game_session_id

        logger.info(f"Játék indítva | player_id: {player_id} | player_name: {player_name} | user_id: {user_id} | game_session_id: {game_session_id} | IP: {ip_address}")

        return redirect(url_for('game_menu'))

    except Exception as e:
        logger.error(f"Játék indítási hiba: {e} | IP: {request.remote_addr}", exc_info=True)
        return redirect(url_for('index', error='Hiba a játék indításakor'))


@game_bp.route('/select-mode', methods=['POST'])
def select_mode():
    #Játékmód kiválasztása
    try:
        game_mode = request.form.get('game_mode', 'color-hunter')
        difficulty = request.form.get('difficulty', 'easy')

        # Validáció
        if game_mode not in ['color-hunter', 'card-match']:
            game_mode = 'color-hunter'
        if difficulty not in ['easy', 'medium', 'hard']:
            difficulty = 'easy'

        session['game_mode'] = game_mode
        session['difficulty'] = difficulty

        # Game session frissítése, ha van aktív session
        if 'game_session_id' in session and 'player_id' in session:
            update_game_session(session['game_session_id'], game_mode, difficulty)

        if game_mode == 'color-hunter':
            return redirect(url_for('game'))
        else:
            return redirect(url_for('game2'))

    except Exception as e:
        logger.error(f"Játékmód választási hiba: {e} | IP: {request.remote_addr}", exc_info=True)
        return redirect(url_for('game_menu', error='Hiba a játékmód választásakor'))


@game_bp.route('/api/game', methods=['POST'])
def new_game():
    #Új játék indítása API végpont
    try:
        data = request.get_json()
        if not data or 'name' not in data:
            logger.warning(f"Új játék API: hiányzó név | IP: {request.remote_addr}")
            return jsonify({'success': False, 'error': 'Hiányzó név'}), 400

        player_name = data['name'].strip()
        game_mode = data.get('game_mode', 'color-hunter')
        difficulty = data.get('difficulty', 'easy')
        ip_address = request.remote_addr

        if not player_name:
            logger.warning(f"Új játék API: érvénytelen név | IP: {ip_address}")
            return jsonify({'success': False, 'error': 'Érvénytelen név'}), 400

        # Ha be van jelentkezve, akkor a user adataival, különben vendégként
        current_user = get_current_user()
        user_id = current_user['user_id'] if current_user else None

        player_id = get_or_create_player(player_name, user_id)

        if not player_id:
            logger.error(f"Játékos létrehozási hiba új játék API-ban | player_name: {player_name} | user_id: {user_id} | IP: {ip_address}")
            return jsonify({'success': False, 'error': 'Hiba a játékos létrehozásakor'}), 500

        # Game session létrehozása
        game_session_id = create_game_session(player_id, game_mode, difficulty)

        logger.info(f"Új játék API: játék indítva | player_id: {player_id} | player_name: {player_name} | game_mode: {game_mode} | difficulty: {difficulty} | game_session_id: {game_session_id} | user_id: {user_id} | IP: {ip_address}")

        return jsonify({
            'success': True,
            'player_id': player_id,
            'player_name': player_name,
            'game_session_id': game_session_id,
            'game_mode': game_mode,
            'difficulty': difficulty,
            'message': 'Játék sikeresen elindítva'
        })

    except Exception as e:
        logger.error(f"Új játék API hiba: {str(e)} | IP: {request.remote_addr}", exc_info=True)
        return jsonify({'success': False, 'error': f'Szerver hiba: {str(e)}'}), 500


@game_bp.route('/api/game/session/end', methods=['POST'])
def end_game_session():
    #Játék session befejezése API végpont - CSAK SESSION LEZÁRÁS
    try:
        data = request.get_json()

        if 'game_session_id' not in data:
            return jsonify({'success': False, 'error': 'Hiányzó game_session_id'}), 400

        game_session_id = int(data['game_session_id'])
        game_time = int(data.get('game_time', 0))

        # Game session lezárása
        if not close_game_session(game_session_id, game_time):
            return jsonify({'success': False, 'error': 'Hiba a játék session lezárásakor'}), 500

        # Session cleanup
        if 'game_session_id' in session:
            session.pop('game_session_id')

        return jsonify({
            'success': True,
            'message': 'Játék session sikeresen lezárva'
        })

    except ValueError:
        return jsonify({'success': False, 'error': 'Érvénytelen adatformátum'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': f'Szerver hiba: {str(e)}'}), 500


@game_bp.route('/api/game/session', methods=['GET'])
def get_game_session():
    #Aktuális játék session lekérése
    conn = None
    cursor = None
    try:
        if 'game_session_id' not in session:
            return jsonify({'success': False, 'error': 'Nincs aktív játék session'}), 404

        game_session_id = session['game_session_id']

        conn = get_db_connect()
        if not conn:
            return jsonify({'success': False, 'error': 'Adatbázis kapcsolat hiba'}), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT gs.*, p.display_name 
            FROM game_sessions gs 
            LEFT JOIN players p ON gs.player_id = p.id 
            WHERE gs.id = %s
        ''', (game_session_id,))

        game_session = cursor.fetchone()

        if not game_session:
            return jsonify({'success': False, 'error': 'Játék session nem található'}), 404

        return jsonify({
            'success': True,
            'game_session': game_session
        })

    except Exception as e:
        return jsonify({'success': False, 'error': f'Szerver hiba: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

# HELPER FUNCTIONS - CSAK SESSION KEZELÉS

def create_game_session(player_id, game_mode, difficulty):
    #Game session létrehozása
    conn = None
    cursor = None
    try:
        conn = get_db_connect()
        if not conn:
            logger.error(f"Adatbázis kapcsolat hiba game session létrehozásakor | player_id: {player_id}")
            return None

        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO game_sessions (player_id, game_mode, difficulty, start_time)
            VALUES (%s, %s, %s, %s)
        ''', (player_id, game_mode, difficulty, datetime.now()))

        game_session_id = cursor.lastrowid
        conn.commit()
        
        logger.debug(f"Game session létrehozva | game_session_id: {game_session_id} | player_id: {player_id} | game_mode: {game_mode} | difficulty: {difficulty}")

        return game_session_id

    except mysql.connector.Error as e:
        logger.error(f"Game session létrehozási hiba: {e} | player_id: {player_id} | game_mode: {game_mode} | difficulty: {difficulty}", exc_info=True)
        if conn and conn.is_connected():
            conn.rollback()
        return None
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def update_game_session(game_session_id, game_mode, difficulty):
    #Game session frissítése
    conn = None
    cursor = None
    try:
        conn = get_db_connect()
        if not conn:
            logger.error(f"Adatbázis kapcsolat hiba game session frissítésénél | game_session_id: {game_session_id}")
            return False

        cursor = conn.cursor()
        cursor.execute('''
            UPDATE game_sessions 
            SET game_mode = %s, difficulty = %s 
            WHERE id = %s
        ''', (game_mode, difficulty, game_session_id))

        conn.commit()
        logger.debug(f"Game session frissítve | game_session_id: {game_session_id} | game_mode: {game_mode} | difficulty: {difficulty}")
        return True

    except mysql.connector.Error as e:
        logger.error(f"Game session frissítési hiba: {e} | game_session_id: {game_session_id}", exc_info=True)
        if conn and conn.is_connected():
            conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def close_game_session(game_session_id, total_time):
    #Game session lezárása
    conn = None
    cursor = None
    try:
        conn = get_db_connect()
        if not conn:
            logger.error(f"Adatbázis kapcsolat hiba game session lezárásakor | game_session_id: {game_session_id}")
            return False

        cursor = conn.cursor()
        cursor.execute('''
            UPDATE game_sessions 
            SET end_time = %s, total_time = %s 
            WHERE id = %s
        ''', (datetime.now(), total_time, game_session_id))

        conn.commit()
        logger.info(f"Game session lezárva | game_session_id: {game_session_id} | total_time: {total_time}s")
        return True
    except mysql.connector.Error as e:
        logger.error(f"Game session lezárási hiba: {e} | game_session_id: {game_session_id}", exc_info=True)
        if conn and conn.is_connected():
            conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


@game_bp.route('/')
def index():
    return render_template('main/menu/index.html')


@game_bp.route('/menu')
def game_menu():
    return render_template('main/menu/gamemode-selector.html')


@game_bp.route('/color-hunter')
def game():
    return render_template('game/color-hunter/color-hunter.html')


@game_bp.route('/card-match')
def game2():
    return render_template('game/card-match/card-match.html')

@game_bp.route('/api/health')
def health():
    from flask import current_app
    from datetime import datetime as _dt
    return jsonify({'status': 'ok', 'database': 'Csatlakozott', 'time': _dt.now().isoformat()})
