from contextlib import contextmanager

import mysql.connector
from mysql.connector import Error
from ..config import Config
from ..utils.logger import get_logger

logger = get_logger('database')

def get_db_connect():
    #Adatbázis kapcsolat létrehozása
    try:
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DATABASE,
            charset=Config.MYSQL_CHARSET,
            autocommit=Config.MYSQL_AUTOCOMMIT,
            connect_timeout=Config.MYSQL_CONNECT_TIMEOUT,
        )
        logger.debug(f"Adatbázis kapcsolat létrehozva: {Config.MYSQL_HOST}/{Config.MYSQL_DATABASE}")
        return connection
    except Error as err:
        logger.error(f"MySQL kapcsolati hiba: {err} | Host: {Config.MYSQL_HOST} | Database: {Config.MYSQL_DATABASE}")
        return None
@contextmanager
def get_db_connection():
    #Context manager for database connections to ensure proper cleanup
    connection = None
    try:
        connection = get_db_connect()
        if not connection:
            raise Exception("Database connection failed")
        yield connection
    except Error as err:
        logger.error(f"Database error in context manager: {err}")
        if connection:
            connection.rollback()
        raise
    finally:
        if connection and connection.is_connected():
            connection.close()
            logger.debug("Adatbázis kapcsolat lezárva")

def init_db():
    #Adatbázis inicializálása
    try:
        logger.info("Adatbázis inicializálás indítva...")
        # Kapcsolat kialakítása adatbázis nélkül
        temp_config = {
            'host': Config.MYSQL_HOST,
            'user': Config.MYSQL_USER,
            'password': Config.MYSQL_PASSWORD,
            'charset': Config.MYSQL_CHARSET,
            'autocommit': Config.MYSQL_AUTOCOMMIT
        }

        connection = mysql.connector.connect(**temp_config)
        cursor = connection.cursor()

        # Adatbázis létrehozása ha nem létezik
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DATABASE} CHARACTER SET {Config.MYSQL_CHARSET} COLLATE {Config.MYSQL_COLLATION}")
        cursor.execute(f"USE {Config.MYSQL_DATABASE}")
        logger.info(f"Adatbázis ellenőrizve/létrehozva: {Config.MYSQL_DATABASE}")

        #user tábla
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            profile_picture VARCHAR(255) DEFAULT 'default_avatar.png',
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP NULL,
            
            INDEX idx_username (username),
            INDEX idx_email (email)
        ) ENGINE = InnoDB DEFAULT CHARSET={Config.MYSQL_CHARSET} COLLATE={Config.MYSQL_COLLATION};
        ''')
        logger.debug("Users tábla ellenőrizve/létrehozva")

        # players tábla
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS players (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT UNIQUE,
                display_name VARCHAR(100) NOT NULL UNIQUE,
                total_games_played INT DEFAULT 0,
                best_score INT DEFAULT 0,
                last_played TIMESTAMP NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
                
                INDEX idx_user_id (user_id),
                INDEX idx_display_name (display_name),
                INDEX idx_best_score (best_score DESC),
                INDEX idx_last_played (last_played DESC),
                UNIQUE KEY unique_display_name (display_name)
            ) ENGINE = InnoDB DEFAULT CHARSET={Config.MYSQL_CHARSET} COLLATE={Config.MYSQL_COLLATION};
            ''')
        logger.debug("Players tábla ellenőrizve/létrehozva")

        #session tábla
        cursor.execute(f'''
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
        logger.debug("Game_sessions tábla ellenőrizve/létrehozva")

        # scores tábla
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS scores (
                id INT AUTO_INCREMENT PRIMARY KEY,
                game_session_id INT NOT NULL,
                player_id INT NOT NULL,
                score INT NOT NULL CHECK (score >= 0),
                game_time INT DEFAULT 0,
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
        logger.debug("Scores tábla ellenőrizve/létrehozva")

        # multiplayer_rooms tábla
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS multiplayer_rooms (
                id INT AUTO_INCREMENT PRIMARY KEY,
                room_code VARCHAR(6) UNIQUE NOT NULL,
                host_player_id INT NOT NULL,
                game_mode VARCHAR(50) DEFAULT 'color-hunter-multiplayer',
                status ENUM('waiting', 'playing', 'finished') DEFAULT 'waiting',
                max_players INT DEFAULT 6,
                current_round INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                started_at TIMESTAMP NULL,
                finished_at TIMESTAMP NULL,
                
                FOREIGN KEY (host_player_id) REFERENCES players(id) ON DELETE CASCADE,
                INDEX idx_room_code (room_code),
                INDEX idx_status (status)
            ) ENGINE = InnoDB DEFAULT CHARSET={Config.MYSQL_CHARSET} COLLATE={Config.MYSQL_COLLATION};
        ''')
        logger.debug("Multiplayer_rooms tábla ellenőrizve/létrehozva")

        # room_players tábla
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS room_players (
                id INT AUTO_INCREMENT PRIMARY KEY,
                room_id INT NOT NULL,
                player_id INT NOT NULL,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                total_score INT DEFAULT 0,
                position INT NULL,
                
                FOREIGN KEY (room_id) REFERENCES multiplayer_rooms(id) ON DELETE CASCADE,
                FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE,
                UNIQUE KEY unique_room_player (room_id, player_id),
                INDEX idx_room_id (room_id),
                INDEX idx_player_id (player_id)
            ) ENGINE = InnoDB DEFAULT CHARSET={Config.MYSQL_CHARSET} COLLATE={Config.MYSQL_COLLATION};
        ''')
        logger.debug("Room_players tábla ellenőrizve/létrehozva")

        # round_results tábla
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS round_results (
                id INT AUTO_INCREMENT PRIMARY KEY,
                room_id INT NOT NULL,
                round_number INT NOT NULL,
                player_id INT NOT NULL,
                is_correct BOOLEAN DEFAULT FALSE,
                response_time_ms INT NULL,
                points_earned INT DEFAULT 0,
                position_in_round INT NULL,
                
                FOREIGN KEY (room_id) REFERENCES multiplayer_rooms(id) ON DELETE CASCADE,
                FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE,
                INDEX idx_room_round (room_id, round_number),
                INDEX idx_player_id (player_id)
            ) ENGINE = InnoDB DEFAULT CHARSET={Config.MYSQL_CHARSET} COLLATE={Config.MYSQL_COLLATION};
        ''')
        logger.debug("Round_results tábla ellenőrizve/létrehozva")

        connection.commit()
        logger.info("Adatbázis és a táblák sikeresen létrehozva/ellenőrizve!")

    except Error as err:
        logger.error(f"MySQL adatbázis inicializálási hiba: {err}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()