from flask import request, jsonify, session
from ..models.database import get_db_connect
from ..models.user import create_player_for_user
from werkzeug.security import generate_password_hash, check_password_hash
from ..utils.validators import validate_registration_data, validate_login_data
from app.config import Config

def register_user():
     #Felhasználó regisztráció - validátorokkal
    try:
        data = request.get_json()

        # Validáció - EGY SORBAN a validators.py segítségével
        is_valid, error_message = validate_registration_data(data)
        if not is_valid:
            return jsonify({'success': False, 'error': error_message}), 400

        username = data['username'].strip()
        email = data['email'].strip()
        password = data['password']
        profile_picture = data.get('profile_picture', Config.DEFAULT_AVATAR)

        # Profilkép validáció


        conn = get_db_connect()
        if not conn:
            return jsonify({'success': False, 'error': 'Adatbázis kapcsolat hiba'}), 500

        cursor = conn.cursor()

        # Ellenőrzés, hogy létezik-e már a felhasználó
        cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'error': 'A felhasználónév vagy email már foglalt'}), 400

        # Felhasználó létrehozása USERS táblában
        password_hash = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, profile_picture) VALUES (%s, %s, %s, %s)",
            (username, email, password_hash, profile_picture)
        )

        user_id = cursor.lastrowid

        # Player létrehozása PLAYERS táblában
        player_id = create_player_for_user(user_id, username)
        if not player_id:
            conn.rollback()
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'error': 'Hiba a játékos profil létrehozásakor'}), 500

        conn.commit()
        cursor.close()
        conn.close()

        # Session beállítása
        session['user_id'] = user_id
        session['username'] = username
        session['player_id'] = player_id
        session['is_authenticated'] = True

        return jsonify({
            'success': True,
            'message': 'Sikeres regisztráció',
            'user_id': user_id,
            'player_id': player_id,
            'username': username,
            'profile_picture': profile_picture
        })

    except Exception as e:
        return jsonify({'success': False, 'error': f'Szerver hiba: {str(e)}'}), 500

def login_user():
    #Felhasználó bejelentkezés - validátorokkal
    try:
        data = request.get_json()

        # Validáció - validators.py segítségével
        is_valid, error_message = validate_login_data(data)
        if not is_valid:
            return jsonify({'success': False, 'error': error_message}), 400

        username = data['username'].strip()
        password = data['password']

        conn = get_db_connect()
        if not conn:
            return jsonify({'success': False, 'error': 'Adatbázis kapcsolat hiba'}), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT u.id, u.username, u.password_hash, u.profile_picture, p.id as player_id 
            FROM users u 
            LEFT JOIN players p ON u.id = p.user_id 
            WHERE u.username = %s AND u.is_active = TRUE
        ''', (username,))

        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if not user or not check_password_hash(user['password_hash'], password):
            return jsonify({'success': False, 'error': 'Hibás felhasználónév vagy jelszó'}), 401

        # Session beállítása
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['player_id'] = user['player_id']
        session['is_authenticated'] = True

        # Utolsó bejelentkezés frissítése
        conn = get_db_connect()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = %s",
            (user['id'],)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Sikeres bejelentkezés',
            'user_id': user['id'],
            'player_id': user['player_id'],
            'username': user['username'],
            'profile_picture': user['profile_picture']
        })

    except Exception as e:
        return jsonify({'success': False, 'error': f'Szerver hiba: {str(e)}'}), 500

def logout_user():
    #Felhasználó kijelentkeztetése
    session.clear()
    return jsonify({'success': True, 'message': 'Sikeres kijelentkezés'})

def get_current_user():
    #Aktuális felhasználó adatainak lekérése
    if 'user_id' in session and session.get('is_authenticated'):
        return {
            'user_id': session['user_id'],
            'username': session['username'],
            'player_id': session.get('player_id')
        }
    return None