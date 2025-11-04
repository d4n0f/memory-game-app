from flask import request, jsonify, render_template, Blueprint, session
from ..models.database import get_db_connect, get_db_connection
from ..models.user import update_player_stats
from ..utils.validators import validate_score_data, validate_player_exists
from datetime import datetime
import mysql.connector

scores_bp = Blueprint('scores', __name__)

@scores_bp.route('/api/save', methods=['POST'])
def save_scores():
    #Eredmények mentése - JAVÍTOTT, GAME SESSION-NEL
    cursor = None
    conn = None
    try:
        data = request.get_json()

        # Validáció
        is_valid, error_message = validate_score_data(data)
        if not is_valid:
            return jsonify({'success': False, 'error': error_message}), 400

        player_id = int(data['player_id'])
        score = int(data['score'])
        game_mode = data['game_mode']
        game_time = int(data.get('game_time', 0))
        rounds_played = int(data.get('rounds_played', 1))
        game_session_id = data.get('game_session_id')
        difficulty = data.get('difficulty','easy')
        score_id = data.get('score_id')
        # Player létezés ellenőrzése
        player_exists, error = validate_player_exists(player_id)
        if not player_exists:
            return jsonify({'success': False, 'error': error}), 404

        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Score mentése
                if game_session_id:
                    cursor.execute(
                        'INSERT INTO scores (game_session_id, player_id, score, rounds_played) VALUES (%s, %s, %s, %s)',
                        (game_session_id, player_id, score, rounds_played)
                    )
                else:
                    cursor.execute(
                        'INSERT INTO game_sessions (player_id, game_mode, difficulty, start_time) VALUES (%s, %s, %s, %s)',
                        (player_id, game_mode, difficulty, datetime.now())
                    )
                    game_session_id = cursor.lastrowid
                    cursor.execute(
                        'INSERT INTO scores (game_session_id, player_id, score, game_time, rounds_played) VALUES (%s, %s, %s, %s, %s)',
                        (game_session_id, player_id, score, game_time, rounds_played)
                    )

                # Player statisztikák frissítése
                update_player_stats(player_id, score)
            conn.commit()

        return jsonify({
            'success': True,
            'message': 'Eredmény sikeresen mentve',
            'score_id': score_id
        })

    except mysql.connector.Error as e:
        if 'conn' in locals() and conn.is_connected():
            conn.rollback()
        return jsonify({'success': False, 'error': f'Adatbázis hiba: {str(e)}'}), 500
    except Exception as e:
        if 'conn' in locals() and conn.is_connected():
            conn.rollback()
        return jsonify({'success': False, 'error': f'Szerver hiba: {str(e)}'}), 500

    finally:
        if cursor:
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

@scores_bp.route('/api/scores', methods=['GET'])
def get_scores():
    # Eredmények lekérése - globális vagy saját (bejelentkezett) nézet
    conn = None
    cursor = None
    try:
        # Nézet kiválasztása: 'global' (alapértelmezett) vagy 'me'
        scope = request.args.get('scope', 'global').lower()

        # Szűrők
        game_mode = request.args.get('game_mode')  # None -> mind
        difficulty = request.args.get('difficulty')  # 'easy'|'medium'|'hard'|None

        # Rendezés
        sort = request.args.get('sort', 'score_desc')
        sort_map = {
            'score_desc': 'score_val DESC, time_val ASC, date_val DESC',
            'score_asc':  'score_val ASC, time_val ASC, date_val DESC',
            'time_asc':   'time_val ASC, score_val DESC, date_val DESC',
            'time_desc':  'time_val DESC, score_val DESC, date_val DESC',
            'date_desc':  'date_val DESC',
            'date_asc':   'date_val ASC',
        }
        order_clause = sort_map.get(sort, sort_map['score_desc'])

        # Lapozás
        limit = min(max(request.args.get('limit', 20, type=int), 1), 100)
        page = max(request.args.get('page', 1, type=int), 1)
        offset = (page - 1) * limit

        conn = get_db_connect()
        if conn is None:
            return jsonify({'success': False, 'error': 'Adatbázis kapcsolat hiba'}), 500

        cursor = conn.cursor(dictionary=True)

        # WHERE feltételek dinamikus építése
        where_clauses = []
        params = []

        if game_mode:
            where_clauses.append('gs.game_mode = %s')
            params.append(game_mode)

        if difficulty:
            where_clauses.append('gs.difficulty = %s')
            params.append(difficulty)

        where_sql = ('WHERE ' + ' AND '.join(where_clauses)) if where_clauses else ''

        if scope == 'me':
            # Csak a bejelentkezett játékos eredményei
            player_id = session.get('player_id')
            if not player_id:
                return jsonify({'success': False, 'error': 'Nincs bejelentkezve'}), 401

            user_where = (' AND ' if where_sql else 'WHERE ') + 's.player_id = %s'
            user_params = params + [player_id]

            # Összes találat száma
            count_sql = f'''
                SELECT COUNT(*) AS total
                FROM scores s
                LEFT JOIN game_sessions gs ON s.game_session_id = gs.id
                {where_sql}{user_where}
            '''
            cursor.execute(count_sql, tuple(user_params))
            total = int((cursor.fetchone() or {'total': 0})['total'])

            # Lista lekérdezés - saját eredmények
            list_sql = f'''
                SELECT 
                    p.display_name,
                    s.score AS score_val,
                    s.game_time AS time_val,
                    s.created_at AS date_val,
                    gs.game_mode,
                    gs.difficulty,
                    s.rounds_played
                FROM scores s
                LEFT JOIN players p ON s.player_id = p.id
                LEFT JOIN game_sessions gs ON s.game_session_id = gs.id
                {where_sql}{user_where}
                ORDER BY {order_clause}
                LIMIT %s OFFSET %s
            '''
            cursor.execute(list_sql, tuple(user_params + [limit, offset]))
            scores = cursor.fetchall() or []

            # Játékos összegzés
            cursor.execute('''
                SELECT 
                    p.id,
                    p.display_name,
                    p.total_games_played,
                    p.best_score,
                    p.last_played
                FROM players p
                WHERE p.id = %s
            ''', (player_id,))
            player = cursor.fetchone() or {}

            # Dátum formázás
            for row in scores:
                if isinstance(row.get('date_val'), datetime):
                    row['date_val'] = row['date_val'].isoformat()
            if player and isinstance(player.get('last_played'), datetime):
                player['last_played'] = player['last_played'].isoformat()

            return jsonify({
                'success': True,
                'scope': 'me',
                'scores': scores,
                'count': len(scores),
                'pagination': {
                    'total': total,
                    'page': page,
                    'limit': limit,
                    'pages': (total + limit - 1) // limit if limit else 1
                },
                'player': player
            })
        else:
            # Globális ranglista: játékosonként (és opcionálisan mód/difficulty szerint) legjobb score
            count_sql = f'''
                SELECT COUNT(*) AS total FROM (
                    SELECT s.player_id
                    FROM scores s
                    LEFT JOIN game_sessions gs ON s.game_session_id = gs.id
                    {where_sql}
                    GROUP BY s.player_id, gs.game_mode, gs.difficulty
                ) t
            '''
            cursor.execute(count_sql, tuple(params))
            total = int((cursor.fetchone() or {'total': 0})['total'])

            list_sql = f'''
                SELECT 
                    p.display_name,
                    gs.game_mode,
                    gs.difficulty,
                    MAX(s.score) AS score_val,
                    MIN(s.game_time) AS time_val,
                    MIN(s.created_at) AS date_val
                FROM scores s
                LEFT JOIN players p ON s.player_id = p.id
                LEFT JOIN game_sessions gs ON s.game_session_id = gs.id
                {where_sql}
                GROUP BY s.player_id, p.display_name, gs.game_mode, gs.difficulty
                ORDER BY {order_clause}
                LIMIT %s OFFSET %s
            '''
            cursor.execute(list_sql, tuple(params + [limit, offset]))
            scores = cursor.fetchall() or []

            for row in scores:
                if isinstance(row.get('date_val'), datetime):
                    row['date_val'] = row['date_val'].isoformat()

            return jsonify({
                'success': True,
                'scope': 'global',
                'scores': scores,
                'count': len(scores),
                'pagination': {
                    'total': total,
                    'page': page,
                    'limit': limit,
                    'pages': (total + limit - 1) // limit if limit else 1
                }
            })
    except Exception as e:
        if conn and conn.is_connected():
            conn.rollback()
        return jsonify({'success': False, 'error': f'Szerver hiba:{str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

@scores_bp.route('/api/players', methods=['GET'])
def get_players():
    #Játékosok lekérése
    cursor = None
    conn = None
    try:
        conn = get_db_connect()
        if conn is None:
            return jsonify({'success': False, 'error': 'Adatbázis kapcsolat hiba'}), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
                    SELECT 
                        p.id, 
                        p.display_name as name, 
                        p.last_played, 
                        p.total_games_played as games_played, 
                        p.best_score as best_score
                    FROM players p
                    ORDER BY p.last_played DESC
                    LIMIT 50
                ''')

        players = cursor.fetchall()
        if not players:
            return jsonify({'success': True, 'players': [], 'count': 0, 'message': 'Nincs elérhető játékos'})

        # Dátum formázás
        for player in players:
            if isinstance(player['last_played'], datetime):
                player['last_played'] = player['last_played'].isoformat()


        return jsonify({'success': True, 'players': players})
    except Exception as e:
        if conn and conn.is_connected():
            conn.rollback()
        return jsonify({'success': False, 'error': f'Adatbázis hiba:{str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
@scores_bp.route('/scores')
def scores():
    return render_template('main/scoreboard/scores.html')