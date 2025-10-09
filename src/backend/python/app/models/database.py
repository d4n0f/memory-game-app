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

            #user tábla
            cursor.execute(t'''CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP NULL,
                
                INDEX idx_username (username),
                INDEX idx_email (email)
            ) ENGINE = InnoDB DEFAULT CHARSET={Config.MYSQL_CHARSET} COLLATE={Config.MYSQL_COLLATION};
            ''')

            # players tábla
            cursor.execute(t'''
                CREATE TABLE IF NOT EXISTS players (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL UNIQUE,
                    display_name VARCHAR(100) NOT NULL,
                    total_games_played INT DEFAULT 0,
                    best_score INT DEFAULT 0,
                    last_played TIMESTAMP NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    
                    INDEX idx_user_id (user_id),
                    INDEX idx_best_score (best_score DESC),
                    INDEX idx_last_played (last_played DESC)
                ) ENGINE = InnoDB DEFAULT CHARSET={Config.MYSQL_CHARSET} COLLATE={Config.MYSQL_COLLATION};
                ''')

            #session tábla
            cursor.execute(t'''
                CREATE TABLE IF NOT EXISTS game_sessions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    player_id INT NOT NULL,
                    game_mode VARCHAR(50) NOT NULL,
                    difficulty ENUM('easy', 'medium', 'hard') DEFAULT 'easy',
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP NULL,
                    total_time INT DEFAULT 0,
                    
                    FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE,
                    
                    INDEX idx_player_id (player_id),
                    INDEX idx_game_mode (game_mode),
                    INDEX idx_start_time (start_time DESC)
                ) ENGINE = InnoDB DEFAULT CHARSET={Config.MYSQL_CHARSET} COLLATE={Config.MYSQL_COLLATION};
            ''')

            # scores tábla
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS scores (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    game_session_id INT NOT NULL,
                    player_id INT NOT NULL,
                    score INT NOT NULL CHECK (score >= 0),
                    rounds_played INT DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    FOREIGN KEY (game_session_id) REFERENCES game_sessions(id) ON DELETE CASCADE,
                    FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE,
                    
                    INDEX idx_game_session_id (game_session_id),
                    INDEX idx_player_id (player_id),
                    INDEX idx_score (score DESC),
                    INDEX idx_created_at (created_at DESC)
                ) ENGINE = InnoDB DEFAULT CHARSET={Config.MYSQL_CHARSET} COLLATE={Config.MYSQL_COLLATION};
                ''')

            connection.commit()
            print("Adatbázis és a táblák sikeresen létrehozva!")

        except Error as err:
            print(f"MySQL adatbázis inicializálási hiba: {err}")
        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()