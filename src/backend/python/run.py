from app.config import Config
from app.models.database import init_db
from app.main import app
from app.routes.multiplayer import get_socketio

if __name__ == '__main__':
    print("Adatbázis inicializálása...")
    init_db()
    print(Config.FRONTEND_DIR)
    print("Flask indítása SocketIO-val...")
    socketio = get_socketio()
    if socketio:
        # Eventlet használata vagy allow_unsafe_werkzeug=True fejlesztési módban
        socketio.run(
            app, 
            debug=Config.FLASK_DEBUG, 
            host=Config.FLASK_HOST, 
            port=Config.FLASK_PORT,
            allow_unsafe_werkzeug=True  # Fejlesztési módban engedélyezve
        )
    else:
        print("Hiba: SocketIO nincs inicializálva!")
        app.run(debug=Config.FLASK_DEBUG, host=Config.FLASK_HOST, port=Config.FLASK_PORT)