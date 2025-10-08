from flask import request, jsonify
from ..models.database import get_db_connect
from datetime import datetime
from ..utils.validators import validate_score_data


def save_scores():
    #Eredmények mentése
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

        conn = get_db_connect()
        if conn is None:
            return jsonify({'success': False, 'error': 'Adatbázis kapcsolat hiba'}), 500

        cursor = conn.cursor()
        cursor.execute("SELECT id FROM players WHERE id=%s", (player_id,))

        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'Játékos nem található'}), 404

        cursor.execute('''
            INSERT INTO scores (player_id, score, game_mode, game_time, rounds_played)
            VALUES (%s, %s, %s, %s, %s)
        ''', (player_id, score, game_mode, game_time, rounds_played))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Eredmény sikeresen mentve',
            'score_id': cursor.lastrowid
        })

    except ValueError:
        return jsonify({'success': False, 'error': 'Érvénytelen adatformátum hiba'}), 400
    except Exception as e:
        if 'conn' in locals() and conn.is_connected():
            conn.rollback()
            cursor.close()
            conn.close()
        return jsonify({'success': False, 'error': f'Adatbázis hiba: {str(e)}'}), 500


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
                SELECT p.name, s.score, s.game_mode, s.game_time, s.rounds_played, s.created_at
                FROM scores s
                JOIN players p ON s.player_id=p.id
                ORDER BY s.score DESC, s.game_time ASC, s.created_at DESC
                LIMIT %s
            ''', (limit,))
        else:
            cursor.execute('''
                SELECT p.name, s.score, s.game_mode, s.game_time, s.rounds_played, s.created_at
                FROM scores s
                JOIN players p ON s.player_id=p.id
                WHERE s.game_mode=%s
                ORDER BY s.score DESC, s.game_time ASC, s.created_at DESC
                LIMIT %s
            ''', (game_mode, limit))

        scores = cursor.fetchall()

        for score in scores:
            if isinstance(score['created_at'], datetime):
                score['created_at'] = score['created_at'].isoformat()

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
    #Játékosok lekérése"""
    try:
        conn = get_db_connect()
        if conn is None:
            return jsonify({'success': False, 'error': 'Adatbázis kapcsolat hiba'}), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT p.id, p.name, p.last_played, COUNT(s.id) as games_played, MAX(s.score) as best_score 
            FROM players p
            LEFT JOIN scores s ON s.player_id=p.id
            GROUP BY p.id
            ORDER BY p.last_played DESC
        ''')

        players = cursor.fetchall()
        cursor.close()
        conn.close()

        return jsonify({'success': True, 'players': players})
    except Exception as e:
        return jsonify({'success': False, 'error': f'Adatbázis hiba:{str(e)}'}), 500