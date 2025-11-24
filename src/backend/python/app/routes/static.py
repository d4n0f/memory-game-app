from flask import send_from_directory, Blueprint, request
from ..config import Config
import os
from ..utils.logger import get_logger

static_bp = Blueprint('static_routes', __name__)
logger = get_logger('static')

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
        logger.warning(f"Color-match kép hiba: {e} | filename: {filename} | IP: {request.remote_addr}")
        return "Képet nem talált", 404

@static_bp.route('/assets/images/<path:filename>')
def serve_general_images(filename):
    try:
        images_dir = os.path.join(Config.FRONTEND_DIR, 'assets', 'images')
        return send_from_directory(images_dir, filename)
    except Exception as e:
        logger.warning(f"Általános kép hiba: {e} | filename: {filename} | IP: {request.remote_addr}")
        return "Képet nem talált", 404