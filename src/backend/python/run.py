from app.config import Config
from app.models.database import init_db
from app.main import app
if __name__ == '__main__':
    print("Adatbázis inicializálása...")
    init_db()
    print(Config.FRONTEND_DIR)
    print("Flask indítása...")
    app.run(debug=Config.FLASK_DEBUG, host=Config.FLASK_HOST, port=Config.FLASK_PORT)