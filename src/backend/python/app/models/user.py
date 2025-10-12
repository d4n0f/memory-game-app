from .database import get_db_connect
from mysql.connector import Error

def create_player_for_user(user_id, username):
    #Játékos létrehozása regisztrált felhasználóhoz - username = display_name
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

        cursor.close()
        conn.close()
        return player_id

    except Error as e:
        print(f"Játékos létrehozási hiba: {e}")
        return None


def create_guest_player(display_name):
    #Vendég játékos létrehozása (user nélkül)
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
        cursor.close()
        conn.close()
        return player_id

    except Error as e:
        print(f"Vendég játékos létrehozási hiba: {e}")
        return None


def get_or_create_player(display_name, user_id=None):
    #Játékos lekérése vagy létrehozása
    try:
        conn = get_db_connect()
        if not conn:
            return None

            cursor = conn.cursor()
            cursor.execute("SELECT id FROM players WHERE name = %s", (player_name,))
            existing_player = cursor.fetchone()

            if existing_player:
                player_id = existing_player[0]
                cursor.execute("UPDATE players SET last_played = CURRENT_TIMESTAMP WHERE id = %s", (player_id,))
            else:
                cursor.execute("INSERT INTO players (name, last_played) VALUES (%s, CURRENT_TIMESTAMP)", (player_name,))
                player_id = cursor.lastrowid

            conn.commit()
            cursor.close()
            conn.close()
            return player_id

        except Error as e:
            print(f"Játékos kezelési hiba: {e}")
            return None