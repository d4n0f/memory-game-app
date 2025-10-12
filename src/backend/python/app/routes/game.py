from flask import request, jsonify, session, redirect, url_for, render_template
from ..models.user import get_or_create_player
from ..models.database import get_db_connect
from .auth import get_current_user
from datetime import datetime
import mysql.connector


def start_game():
     #Játék indítása a főoldalról
    try:
        player_name = request.form.get('player_name', '').strip()

        if not player_name:
            return redirect(url_for('index', error='Nincs név megadva'))

        if not (1 <= len(player_name) <= 50):
            return redirect(url_for('index', error='A név hossza 1–30 karakter között lehet.'))

        # Ha be van jelentkezve, akkor a user adataival, különben vendégként
        current_user = get_current_user()
        user_id = current_user['user_id'] if current_user else None

        player_id = get_or_create_player(player_name, user_id)

        if not player_id:
            return redirect(url_for('index', error='Hiba a játékos létrehozásakor'))

        session['player_name'] = player_name
        session['player_id'] = player_id

        # Game session létrehozása
        game_session_id = create_game_session(player_id, 'color-hunter', 'easy')
        session['game_session_id'] = game_session_id

        return redirect(url_for('game_menu'))

    except Exception as e:
        print(f"Játék indítási hiba: {e}")
        return redirect(url_for('index', error='Hiba a játék indításakor'))


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
        print(f"Játékmód választási hiba: {e}")
        return redirect(url_for('game_menu', error='Hiba a játékmód választásakor'))


def new_game():
    #Új játék indítása API végpont
    try:
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'success': False, 'error': 'Hiányzó név'}), 400

        player_name = data['name'].strip()
        game_mode = data.get('game_mode', 'color-hunter')
        difficulty = data.get('difficulty', 'easy')

        if not player_name:
            return jsonify({'success': False, 'error': 'Érvénytelen név'}), 400

        # Ha be van jelentkezve, akkor a user adataival, különben vendégként
        current_user = get_current_user()
        user_id = current_user['user_id'] if current_user else None

        player_id = get_or_create_player(player_name, user_id)

        if not player_id:
            return jsonify({'success': False, 'error': 'Hiba a játékos létrehozásakor'}), 500

        # Game session létrehozása
        game_session_id = create_game_session(player_id, game_mode, difficulty)

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
        return jsonify({'success': False, 'error': f'Szerver hiba: {str(e)}'}), 500


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


def get_game_session():
    #Aktuális játék session lekérése
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
        cursor.close()
        conn.close()

        if not game_session:
            return jsonify({'success': False, 'error': 'Játék session nem található'}), 404

        return jsonify({
            'success': True,
            'game_session': game_session
        })

    except Exception as e:
        return jsonify({'success': False, 'error': f'Szerver hiba: {str(e)}'}), 500


# HELPER FUNCTIONS - CSAK SESSION KEZELÉS

def create_game_session(player_id, game_mode, difficulty):
    #Game session létrehozása
    try:
        conn = get_db_connect()
        if not conn:
            return None

        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO game_sessions (player_id, game_mode, difficulty, start_time)
            VALUES (%s, %s, %s, %s)
        ''', (player_id, game_mode, difficulty, datetime.now()))

        game_session_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()

        return game_session_id

    except mysql.connector.Error as e:
        print(f"Game session létrehozási hiba: {e}")
        return None


def update_game_session(game_session_id, game_mode, difficulty):
    #Game session frissítése
    try:
        conn = get_db_connect()
        if not conn:
            return False

        cursor = conn.cursor()
        cursor.execute('''
            UPDATE game_sessions 
            SET game_mode = %s, difficulty = %s 
            WHERE id = %s
        ''', (game_mode, difficulty, game_session_id))

        conn.commit()
        cursor.close()
        conn.close()
        return True

    except mysql.connector.Error as e:
        print(f"Game session frissítési hiba: {e}")
        return False


def close_game_session(game_session_id, total_time):
    #Game session lezárása
    try:
        conn = get_db_connect()
        if not conn:
            return False

        cursor = conn.cursor()
        cursor.execute('''
            UPDATE game_sessions 
            SET end_time = %s, total_time = %s 
            WHERE id = %s
        ''', (datetime.now(), total_time, game_session_id))

        conn.commit()
        cursor.close()
        conn.close()
        return True

    except mysql.connector.Error as e:
        print(f"Game session lezárási hiba: {e}")
        return False


def index():
    return render_template('main/menu/index.html')


def game_menu():
    return render_template('main/menu/gamemode-selector.html')


def game():
    return render_template('game/color-hunter/color-hunter.html')


def game2():
    return render_template('game/card-match/card-match.html')


def scores():
    return render_template('main/scoreboard/scores.html')