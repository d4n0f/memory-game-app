import os
from dotenv import load_dotenv

load_dotenv()

class Config:

    # MySQL konfiguráció
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'admin')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'memory_game')
    MYSQL_CHARSET = os.getenv('MYSQL_CHARSET', 'utf8mb4')
    MYSQL_COLLATION = os.getenv('MYSQL_COLLATION', 'utf8mb4_hungarian_ci')
    MYSQL_AUTOCOMMIT = os.getenv('MYSQL_AUTOCOMMIT', 'True').lower() == 'true'
    MYSQL_CONNECT_TIMEOUT = int(os.getenv('MYSQL_CONNECT_TIMEOUT','30'))



    # Flask konfiguráció
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-only-change-me')

    # File path konfiguráció
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')
    
    # Logs könyvtár létrehozása ha nem létezik
    LOGS_DIR = os.path.join(BASE_DIR, 'logs')
    os.makedirs(LOGS_DIR, exist_ok=True)

    DEFAULT_AVATAR = os.getenv('DEFAULT_AVATAR', 'default_avatar.png')

    # Logolási konfiguráció
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FILE = os.path.join(LOGS_DIR, 'app.log')
    LOG_ERROR_FILE = os.path.join(LOGS_DIR, 'error.log')
    LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', '10485760'))  # 10MB alapértelmezett
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', '5'))  # 5 backup fájl
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'