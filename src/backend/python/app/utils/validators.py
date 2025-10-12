import re
from werkzeug.security import check_password_hash

from .helpers import is_valid_difficulty, is_valid_game_mode, validate_entity_exists
from ..models.database import get_db_connect  # Új import


def validate_email(email, check_unique=False):
    #Email validáció
    if not email or not isinstance(email, str):
        return False, 'Érvénytelen email cím'

    email = email.strip()
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False, 'Érvénytelen email formátum'

    if check_unique:
        try:
            conn = get_db_connect()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            exists = cursor.fetchone()
            cursor.close()
            conn.close()
            if exists:
                return False, 'Ez az email már használatban van'
        except Exception:
            return False, 'Adatbázis hiba az email ellenőrzés során'

    return True, None

def validate_username(username, check_unique=False):
    #Felhasználónév validáció
    if not username or not isinstance(username, str):
        return False, 'Érvénytelen felhasználónév'

    username = username.strip()

    if len(username) < 3:
        return False, 'A felhasználónévnek legalább 3 karakter hosszúnak kell lennie'

    if len(username) > 50:
        return False, 'A felhasználónév maximum 50 karakter hosszú lehet'

    # Csak betűk, számok, aláhúzás
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, 'A felhasználónév csak betűket, számokat és aláhúzást tartalmazhat'

    if check_unique:
        try:
            conn = get_db_connect()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            exists = cursor.fetchone()
            cursor.close()
            conn.close()
            if exists:
                return False, 'Ez az username már használatban van'
        except Exception:
            return False, 'Adatbázis hiba az username ellenőrzés során'
    return True, None


def validate_password(password, confirm_password=None):
    #Jelszó validáció - erős jelszókövetelmények
    if not password or not isinstance(password, str):
        return False, 'Érvénytelen jelszó'

    # Minimum 8 karakter
    if len(password) < 8:
        return False, 'A jelszónak legalább 8 karakter hosszúnak kell lennie'

    # Kisbetű ellenőrzés
    if not re.search(r'[a-z]', password):
        return False, 'A jelszónak tartalmaznia kell legalább egy kisbetűt'

    # Nagybetű ellenőrzés
    if not re.search(r'[A-Z]', password):
        return False, 'A jelszónak tartalmaznia kell legalább egy nagybetűt'

    # Szám ellenőrzés
    if not re.search(r'[0-9]', password):
        return False, 'A jelszónak tartalmaznia kell legalább egy számot'

    # Speciális karakter ellenőrzés (opcionális, de ajánlott)
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, 'A jelszónak tartalmaznia kell legalább egy speciális karaktert (!@#$%^&* stb.)'

    # Jelszó egyezés ellenőrzése (ha van confirm_password)
    if confirm_password is not None and password != confirm_password:
        return False, 'A jelszavak nem egyeznek'

    return True, None


def validate_password_strength(password):
    #Jelszó erősség ellenőrzése (csak információs célra)
    score = 0

    # Hossz
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1

    # Karaktertípusok
    if re.search(r'[a-z]', password):
        score += 1
    if re.search(r'[A-Z]', password):
        score += 1
    if re.search(r'[0-9]', password):
        score += 1
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 1

    # Erősség értékelés
    if score <= 2:
        return 'gyenge'
    elif score <= 4:
        return 'közepes'
    else:
        return 'erős'


def validate_registration_data(data):
    #Regisztrációs adatok validálása adatbázis ellenőrzéssel
    required_fields = ['username', 'email', 'password', 'confirm_password']

    for field in required_fields:
        if field not in data or not data[field] or not data[field].strip():
            return False, f'Hiányzó mező: {field}'

    # Felhasználónév validáció + egyediség ellenőrzés
    is_valid, error = validate_username(data['username'],check_unique=True)
    if not is_valid:
        return False, error

    # Email validáció + egyediség ellenőrzés
    is_valid, error = validate_email(data['email'],check_unique=True)
    if not is_valid:
        return False, error

    # Jelszó validáció
    is_valid, error = validate_password(data['password'], data['confirm_password'])
    if not is_valid:
        return False, error

    return True, None


def validate_login_data(data):
    #Bejelentkezési adatok validálása
    if 'username' not in data or not data['username'] or not data['username'].strip():
        return False, 'Hiányzó felhasználónév'

    if 'password' not in data or not data['password']:
        return False, 'Hiányzó jelszó'

    return True, None


def validate_user_exists(username):
     #Ellenőrzi, hogy a felhasználó létezik-e az adatbázisban
    return validate_entity_exists('users', username,'username')


def validate_player_exists(player_id):
    #Ellenőrzi, hogy a játékos létezik-e
    return validate_entity_exists('players', player_id,'player_id')

def validate_score_data(data):
    #Score adatok validálása
    required_fields = ['player_id', 'score', 'game_mode', 'game_time', 'rounds_played']

    for field in required_fields:
        if field not in data:
            return False, f'Hiányzó mező: {field}'

    try:
        player_id = int(data['player_id'])
        score = int(data['score'])
        game_time = int(data.get('game_time', 0))
        rounds_played = int(data.get('rounds_played', 1))

        if score < 0 or game_time < 0 or rounds_played < 1:
            return False, 'Érvénytelen érték'

        if data['difficulty'] not in ['easy', 'medium', 'hard']:
            return False, 'Érvénytelen játékmód'

        return True, None

    except (ValueError, TypeError):
        return False, 'Érvénytelen adatformátum'