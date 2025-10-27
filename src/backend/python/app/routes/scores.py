from flask import request, jsonify
from ..models.database import get_db_connect
from ..models.user import update_player_stats
from ..utils.validators import validate_score_data, validate_player_exists
from datetime import datetime
import mysql.connector

def save_scores():
    #Eredmények mentése - JAVÍTOTT, GAME SESSION-NEL
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

        conn = get_db_connect()
        if conn is None:
            return jsonify({'success': False, 'error': 'Adatbázis kapcsolat hiba'}), 500

        cursor = conn.cursor()

        # Score mentése
        if game_session_id:
            # Ha van game_session_id, akkor azt használjuk
            cursor.execute('''
                INSERT INTO scores (game_session_id, player_id, score, rounds_played)
                VALUES (%s, %s, %s, %s)
            ''', (game_session_id, player_id, score, rounds_played))
        else:
            # Ha nincs game_session_id, akkor klasszikus módon
            cursor.execute('''
                INSERT INTO game_sessions (player_id, game_mode, difficulty, start_time)
                VALUES (%s, %s, %s, %s)
            ''', (player_id, game_mode, difficulty, datetime.now()))
            game_session_id = cursor.lastrowid

        # Player statisztikák frissítése
        update_player_stats(player_id, score)

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Eredmény sikeresen mentve',
            'score_id': score_id
        })

    except mysql.connector.Error as e:
        if 'conn' in locals() and conn.is_connected():
            conn.rollback()
            cursor.close()
            conn.close()
        return jsonify({'success': False, 'error': f'Adatbázis hiba: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': f'Szerver hiba: {str(e)}'}), 500

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals() and conn.is_connected(): conn.close()

def get_scores():
    #Eredmények lekérése
    try:
        game_mode = request.args.get('game_mode', 'all')
        limit = int(request.args.get('limit', 20))

        conn = get_db_connect()
        if conn is None:
            return jsonify({'success': False, 'error': 'Adatbázis kapcsolat hiba'}), 500

        cursor = conn.cursor(dictionary=True)

        if game_mode == 'all':
            cursor.execute('''
                SELECT p.display_name, s.score, gs.game_mode,gs.difficulty, s.game_time, s.rounds_played, s.created_at
                FROM scores s
                LEFT JOIN players p ON s.player_id=p.id
                LEFT JOIN game_sessions gs ON s.game_session_id = gs.id
                ORDER BY s.score DESC, s.game_time ASC, s.created_at DESC
                LIMIT %s
            ''', (limit,))
        else:
            cursor.execute('''
                SELECT p.display_name, s.score, gs.game_mode,gs.difficulty, s.game_time, s.rounds_played, s.created_at
                FROM scores s
                LEFT JOIN players p ON s.player_id=p.id
                LEFT JOIN game_sessions gs ON s.game_session_id = gs.id
                WHERE gs.game_mode=%s
                ORDER BY s.score DESC, s.game_time ASC, s.created_at DESC
                LIMIT %s
            ''', (game_mode, limit))

        scores = cursor.fetchall()

        for score in scores:
            if isinstance(score['created_at'], datetime):
                score['created_at'] = score['created_at'].isoformat()

        if not scores:
            return jsonify({'success': True, 'scores': [], 'count': 0, 'message': 'Nincs elérhető eredmény'})

        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'scores': scores,
            'count': len(scores)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': f'Szerver hiba:{str(e)}'}), 500


def get_players():
    #Játékosok lekérése
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

        cursor.close()
        conn.close()

        return jsonify({'success': True, 'players': players})
    except Exception as e:
        return jsonify({'success': False, 'error': f'Adatbázis hiba:{str(e)}'}), 500