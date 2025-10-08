import mysql.connector
from mysql.connector import Error
from src.backend.python.app.config import *


def get_db_connect():
        #Adatbázis kapcsolat létrehozása
        try:
            connection = mysql.connector.connect(
                host=Config.MYSQL_HOST,
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD,
                database=Config.MYSQL_DATABASE,
                charset=Config.MYSQL_CHARSET
            )
            return connection
        except Error as err:
            print(f"MySQL kapcsolati hiba: {err}")
            return None

def init_db():
        #Adatbázis inicializálása
        try:
            # Kapcsolat kialakítása adatbázis nélkül
            temp_config = {
                'host': Config.MYSQL_HOST,
                'user': Config.MYSQL_USER,
                'password': Config.MYSQL_PASSWORD,
                'charset': Config.MYSQL_CHARSET
            }

            connection = mysql.connector.connect(**temp_config)
            cursor = connection.cursor()

            # Adatbázis létrehozása ha nem létezik
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DATABASE} CHARACTER SET {Config.MYSQL_CHARSET} COLLATE {Config.MYSQL_COLLATION}")
            cursor.execute(f"USE {Config.MYSQL_DATABASE}")

            # players tábla
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS players (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_played TIMESTAMP NULL,
                    is_active BOOLEAN DEFAULT TRUE
                ) ENGINE = InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                ''')

            # scores tábla
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS scores (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    player_id INT NOT NULL,
                    score INT NOT NULL CHECK (score >= 0),
                    game_mode VARCHAR(100) NOT NULL,
                    difficulty Enum('easy', 'medium', 'hard') DEFAULT 'easy',
                    game_time INT DEFAULT 0 CHECK (game_time >= 0),
                    rounds_played INT DEFAULT 1 CHECK (rounds_played >= 1),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE
                ) ENGINE = InnoDB DEFAULT CHARSET={Config.MYSQL_CHARSET} COLLATE={Config.MYSQL_COLLATION}
                ''')

            connection.commit()
            print("Adatbázis és a táblák sikeresen létrehozva!")

        except Error as err:
            print(f"MySQL adatbázis inicializálási hiba: {err}")
        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()