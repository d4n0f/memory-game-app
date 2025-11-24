from .database import get_db_connect
from mysql.connector import Error
from ..utils.logger import get_logger

logger = get_logger('user')

def create_player_for_user(user_id, username):
    #Játékos létrehozása regisztrált felhasználóhoz - username = display_name
    conn = None
    cursor = None
    try:
        conn = get_db_connect()
        if not conn:
            logger.error(f"Adatbázis kapcsolat hiba játékos létrehozásnál: user_id={user_id}, username={username}")
            return None

        cursor = conn.cursor()

        # Játékos létrehozása a felhasználó nevével
        cursor.execute(
            "INSERT INTO players (user_id, display_name) VALUES (%s, %s)",
            (user_id, username)  # username lesz a display_name
        )
        player_id = cursor.lastrowid

        conn.commit()
        logger.info(f"Játékos létrehozva felhasználóhoz: user_id={user_id}, player_id={player_id}, display_name={username}")
        return player_id

    except Error as e:
        logger.error(f"Játékos létrehozási hiba: {e} | user_id={user_id}, username={username}")
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
            logger.error(f"Adatbázis kapcsolat hiba vendég játékos létrehozásnál: display_name={display_name}")
            return None

        cursor = conn.cursor()

        # Vendég játékos létrehozása (user_id = NULL)
        cursor.execute(
            "INSERT INTO players (display_name) VALUES (%s)",
            (display_name,)
        )
        player_id = cursor.lastrowid

        conn.commit()
        logger.info(f"Vendég játékos létrehozva: player_id={player_id}, display_name={display_name}")
        return player_id

    except Error as e:
        logger.error(f"Vendég játékos létrehozási hiba: {e} | display_name={display_name}")
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
            logger.error(f"Adatbázis kapcsolat hiba játékos lekérésnél: display_name={display_name}, user_id={user_id}")
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
            logger.debug(f"Létező játékos lekérve: player_id={player_id}, display_name={display_name}")
        else:
            # 2. CREATE külön kapcsolatban
            if user_id:
                player_id = create_player_for_user(user_id, display_name)
            else:
                player_id = create_guest_player(display_name)
            logger.info(f"Új játékos létrehozva: player_id={player_id}, display_name={display_name}, user_id={user_id}")

        return player_id

    except Error as e:
        logger.error(f"Játékos kezelési hiba: {e} | display_name={display_name}, user_id={user_id}")
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
            logger.error(f"Adatbázis kapcsolat hiba player lekérésnél: user_id={user_id}")
            return None

        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, display_name, total_games_played, best_score, last_played FROM players WHERE user_id = %s",
            (user_id,)
        )

        player = cursor.fetchone()
        
        if player:
            logger.debug(f"Player lekérve user_id alapján: user_id={user_id}, player_id={player.get('id')}")
        else:
            logger.warning(f"Player nem található user_id alapján: user_id={user_id}")

        return player
    except Error as e:
        logger.error(f"Játékos lekérési hiba: {e} | user_id={user_id}")
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
            logger.error(f"Adatbázis kapcsolat hiba statisztika frissítésnél: player_id={player_id}, score={score}")
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
        logger.info(f"Player statisztikák frissítve: player_id={player_id}, score={score}")
        return True
    except Error as e:
        logger.error(f"Player stat frissítési hiba: {e} | player_id={player_id}, score={score}")
        if conn and conn.is_connected():
            conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()