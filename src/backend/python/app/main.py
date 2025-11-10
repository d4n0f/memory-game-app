from flask import jsonify, request
from . import create_app
from .utils.logger import get_logger
import traceback

app = create_app()
logger = get_logger('app')

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    logger.warning(f"404 Not Found: {request.method} {request.path} | IP: {request.remote_addr}")
    return jsonify({'success': False, 'error': 'A kért erőforrás nem található'}), 404

@app.errorhandler(500)
def internal_server_error(e):
    logger.error(
        f"500 Internal Server Error: {request.method} {request.path} | "
        f"IP: {request.remote_addr} | "
        f"Error: {str(e)} | "
        f"Traceback: {traceback.format_exc()}"
    )
    return jsonify({'success': False, 'error': 'Belső szerver hiba'}), 500

@app.errorhandler(405)
def method_not_allowed(e):
    logger.warning(
        f"405 Method Not Allowed: {request.method} {request.path} | "
        f"IP: {request.remote_addr}"
    )
    return jsonify({'success': False, 'error': 'Nem engedélyezett HTTP metódus'}), 405
