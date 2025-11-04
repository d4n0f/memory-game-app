from flask import request, jsonify, session, render_template, Blueprint
from ..models.database import get_db_connect
from ..models.user import create_player_for_user
from werkzeug.security import generate_password_hash, check_password_hash
from ..config import Config
from ..utils.validators import validate_registration_data, validate_login_data, validate_username, validate_password

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/register', methods=['POST'])
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

        # Player létrehozása PLAYERS táblában - SAME CONNECTION
        cursor.execute(
            "INSERT INTO players (user_id, display_name) VALUES (%s, %s)",
            (user_id, username)
        )
        player_id = cursor.lastrowid

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
        # Proper cleanup on error
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.rollback()
            conn.close()
        return jsonify({'success': False, 'error': f'Szerver hiba: {str(e)}'}), 500

@auth_bp.route('/api/login', methods=['POST'])
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

@auth_bp.route('/api/logout', methods=['POST'])
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

@auth_bp.route('/api/current-user', methods=['GET'])
def current_user_endpoint():
    user = get_current_user()
    if user:
        return jsonify({'success': True, 'user': user})
    return jsonify({'success': False, 'error': 'Nincs bejelentkezve'}), 401

@auth_bp.route('/api/user/update', methods=['PATCH'])
def update_user():
    if not session.get('is_authenticated') or not session.get('user_id'):
        return jsonify({'success': False, 'error': 'Nincs bejelentkezve'}), 401

    user_id = session['user_id']
    data = request.get_json() or {}

    new_username = (data.get('username') or '').strip()
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    if not new_username and not new_password:
        return jsonify({'success': False, 'error': 'Nincs változtatandó adat'}), 400

    conn = None
    cursor = None
    try:
        conn = get_db_connect()
        if not conn:
            return jsonify({'success': False, 'error': 'Adatbázis kapcsolat hiba'}), 500
        cursor = conn.cursor(dictionary=True)

        # Aktuális user lekérés
        cursor.execute('SELECT id, username, password_hash FROM users WHERE id = %s', (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({'success': False, 'error': 'Felhasználó nem található'}), 404

        updates = []
        params = []

        # Felhasználónév módosítás validációval + egyediség ellenőrzés, ha tényleg változik
        if new_username and new_username != user['username']:
            ok, err = validate_username(new_username, check_unique=True)
            if not ok:
                return jsonify({'success': False, 'error': err}), 400
            updates.append('username = %s')
            params.append(new_username)

        # Jelszó módosítás validációval
        if new_password:
            if not current_password:
                return jsonify({'success': False, 'error': 'A jelenlegi jelszó megadása kötelező'}), 400
            # Ellenőrzés: jelenlegi jelszó helyes-e
            if not check_password_hash(user['password_hash'], current_password):
                return jsonify({'success': False, 'error': 'A jelenlegi jelszó hibás'}), 401
            # Új jelszó erősség validáció
            ok, err = validate_password(new_password)
            if not ok:
                return jsonify({'success': False, 'error': err}), 400
            updates.append('password_hash = %s')
            params.append(generate_password_hash(new_password))

        if not updates:
            return jsonify({'success': True, 'message': 'Nincs módosítás'}), 200

        # Frissítés users táblában
        set_clause = ', '.join(updates)
        sql = f'UPDATE users SET {set_clause} WHERE id = %s'
        params.append(user_id)
        cursor.execute(sql, tuple(params))

        # Ha a username változott: players.display_name szinkron + session update
        if new_username and new_username != user['username']:
            cursor.execute('UPDATE players SET display_name = %s WHERE user_id = %s', (new_username, user_id))
            session['username'] = new_username

        conn.commit()

        return jsonify({'success': True, 'message': 'Felhasználói adatok frissítve',
                        'user': {'id': user_id, 'username': new_username or user['username']}})
    except Exception as e:
        if conn and conn.is_connected():
            conn.rollback()
        return jsonify({'success': False, 'error': f'Szerver hiba: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

@auth_bp.route('/login')
def login():
    return render_template('main/menu/login.html')

@auth_bp.route('/registration')
def registration():
    return render_template('main/menu/registration.html')