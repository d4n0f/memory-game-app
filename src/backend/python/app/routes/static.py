from flask import send_from_directory, Blueprint
from ..config import Config
import os

static_bp = Blueprint('static_routes', __name__)

@static_bp.route('/styles/<path:filename>')
def serve_css(filename):
    return send_from_directory(os.path.join(Config.FRONTEND_DIR, 'styles'), filename)

@static_bp.route('/scripts/<path:filename>')
def serve_js(filename):
    return send_from_directory(os.path.join(Config.FRONTEND_DIR, 'scripts'), filename)

@static_bp.route('/assets/images/color-match/<path:filename>')
def serve_color_match_images(filename):
    try:
        images_dir = os.path.join(Config.FRONTEND_DIR, 'assets', 'images', 'color-match')
        return send_from_directory(images_dir, filename)
    except Exception as e:
        print(f"Color-match kép hiba: {e}")
        return "Képet nem talált", 404

@static_bp.route('/assets/images/<path:filename>')
def serve_general_images(filename):
    try:
        images_dir = os.path.join(Config.FRONTEND_DIR, 'assets', 'images')
        return send_from_directory(images_dir, filename)
    except Exception as e:
        print(f"Általános kép hiba: {e}")
        return "Képet nem talált", 404