from flask import Flask
from .config import Config

# Import blueprints
from .routes.auth import auth_bp
from .routes.game import game_bp
from .routes.scores import scores_bp
from .routes.static import static_bp


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

    return app

