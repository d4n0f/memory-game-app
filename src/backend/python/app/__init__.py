from flask import Flask, request, g, session
from .config import Config
import time
import traceback

# Import blueprints
from .routes.auth import auth_bp
from .routes.game import game_bp
from .routes.scores import scores_bp
from .routes.static import static_bp
from .routes.multiplayer import multiplayer_bp, init_socketio

# Logger inicializálás
from .utils.logger import setup_logger

logger = setup_logger('app')


def create_app(config_object: type = Config) -> Flask:
    app = Flask(__name__, static_folder=config_object.FRONTEND_DIR,
                template_folder=config_object.FRONTEND_DIR)
    app.config.from_object(config_object)
    app.secret_key = config_object.FLASK_SECRET_KEY

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(game_bp)
    app.register_blueprint(scores_bp)
    app.register_blueprint(static_bp)
    app.register_blueprint(multiplayer_bp)
    
    # SocketIO inicializálása
    init_socketio(app)

    # Middleware: Request logging
    @app.before_request
    def before_request():
        g.start_time = time.time()
        # API kérések logolása (kivéve statikus fájlok)
        if not request.path.startswith('/static') and not request.path.startswith('/assets'):
            user_id = session.get('user_id') if session else None
            logger.info(
                f"Request: {request.method} {request.path} | "
                f"IP: {request.remote_addr} | "
                f"User ID: {user_id if user_id else 'Anonymous'}"
            )

    @app.after_request
    def after_request(response):
        # Válaszidő számolása
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            # API válaszok logolása (kivéve statikus fájlok)
            if not request.path.startswith('/static') and not request.path.startswith('/assets'):
                log_level = 'warning' if response.status_code >= 400 else 'info'
                getattr(logger, log_level)(
                    f"Response: {request.method} {request.path} | "
                    f"Status: {response.status_code} | "
                    f"Duration: {duration:.3f}s"
                )
        return response

    @app.teardown_request
    def teardown_request(exception):
        if exception:
            logger.error(
                f"Exception in request: {request.method} {request.path} | "
                f"Error: {str(exception)} | "
                f"Traceback: {traceback.format_exc()}"
            )

    logger.info("Flask alkalmazás inicializálva")
    return app

