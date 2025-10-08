from .database import get_db_connect

def create_or_get_player(player_name):
        #Játékos létrehozása vagy lekérése
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