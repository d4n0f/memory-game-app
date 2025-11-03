from .database import get_db_connect
from mysql.connector import Error

def create_player_for_user(user_id, username):
    #Játékos létrehozása regisztrált felhasználóhoz - username = display_name
    conn = None
    cursor = None
    try:
        conn = get_db_connect()
        if not conn:
            return None

        cursor = conn.cursor()

        # Játékos létrehozása a felhasználó nevével
        cursor.execute(
            "INSERT INTO players (user_id, display_name) VALUES (%s, %s)",
            (user_id, username)  # username lesz a display_name
        )
        player_id = cursor.lastrowid

        conn.commit()
        return player_id

    except Error as e:
        print(f"Játékos létrehozási hiba: {e}")
        if conn and conn.is_connected():
            conn.rollback()
        return None
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def create_guest_player(display_name):
    #Vendég játékos létrehozása (user nélkül)
    conn = None
    cursor = None
    try:
        conn = get_db_connect()
        if not conn:
            return None

        cursor = conn.cursor()

        # Vendég játékos létrehozása (user_id = NULL)
        cursor.execute(
            "INSERT INTO players (display_name) VALUES (%s)",
            (display_name,)
        )
        player_id = cursor.lastrowid

        conn.commit()
        return player_id

    except Error as e:
        print(f"Vendég játékos létrehozási hiba: {e}")
        if conn and conn.is_connected():
            conn.rollback()
        return None
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def get_or_create_player(display_name, user_id=None):
    #Játékos lekérése vagy létrehozása
    conn = None
    cursor = None
    try:
        conn = get_db_connect()
        if not conn:
            return None

        cursor = conn.cursor()

        # Először megpróbáljuk megtalálni a display_name alapján
        cursor.execute("SELECT id FROM players WHERE display_name = %s", (display_name,))
        existing_player = cursor.fetchone()

        if existing_player:
            player_id = existing_player[0]
            cursor.execute(
                "UPDATE players SET last_played = CURRENT_TIMESTAMP WHERE id = %s",
                (player_id,)
            )
            conn.commit()
        else:
            # 2. CREATE külön kapcsolatban
            if user_id:
                player_id = create_player_for_user(user_id, display_name)
            else:
                player_id = create_guest_player(display_name)

        return player_id

    except Error as e:
        print(f"Játékos kezelési hiba: {e}")
        if conn and conn.is_connected():
            conn.rollback()
        return None
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def get_player_by_user_id(user_id):
    # Player lekérése user_id alapján
    conn = None
    cursor = None
    try:
        conn = get_db_connect()
        if not conn:
            return None

        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, display_name, total_games_played, best_score, last_played FROM players WHERE user_id = %s",
            (user_id,)
        )

        player = cursor.fetchone()

        return player
    except Error as e:
        print(f"Játékos lekérési hiba: {e}")
        if conn and conn.is_connected():
            conn.rollback()
        return None
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def update_player_stats(player_id, score):
    # Player statisztikák frissítése
    conn = None
    cursor = None
    try:
        conn = get_db_connect()
        if not conn:
            return False

        cursor = conn.cursor()

        # Total games növelése, best_score frissítése ha szükséges, last_played beállítása
        cursor.execute('''
            UPDATE players 
            SET total_games_played = total_games_played + 1,
                best_score = GREATEST(best_score, %s),
                last_played = CURRENT_TIMESTAMP
            WHERE id = %s
        ''', (score, player_id))

        conn.commit()

        return True
    except Error as e:
        print(f"Player stat frissítési hiba: {e}")
        if conn and conn.is_connected():
            conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()