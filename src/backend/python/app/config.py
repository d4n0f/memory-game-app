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
    MYSQL_AUTOCOMMIT = os.getenv('MYSQL_AUTOCOMMIT', 'True')
    MYSQL_CONNECT_TIMEOUT = int(os.getenv('MYSQL_CONNECT_TIMEOUT','30'))



    # Flask konfiguráció
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    # File path konfiguráció
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')

    DEFAULT_AVATAR = os.getenv('DEFAULT_AVATAR', 'default_avatar.png')