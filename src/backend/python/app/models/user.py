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

        # Először megpróbáljuk megtalálni a display_name alapján
        cursor.execute("SELECT id FROM players WHERE display_name = %s", (display_name,))
        existing_player = cursor.fetchone()

        if existing_player:
            player_id = existing_player[0]
            update_conn = get_db_connect()
            update_cursor = update_conn.cursor()
            update_cursor.execute(
                "UPDATE players SET last_played = CURRENT_TIMESTAMP WHERE id = %s",
                (player_id,)
            )
            update_cursor.close()
            update_conn.close()
        else:
            # 2. CREATE külön kapcsolatban
            if user_id:
                player_id = create_player_for_user(user_id, display_name)
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

def get_player_by_user_id(user_id):
    # Player lekérése user_id alapján"""
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
        cursor.close()
        conn.close()

        return player
    except Error as e:
        print(f"Játékos lekérési hiba: {e}")
        return None


def update_player_stats(player_id, score):
    # Player statisztikák frissítése"""
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
        cursor.close()
        conn.close()

        return True
    except Error as e:
        print(f"Player stat frissítési hiba: {e}")
        return False