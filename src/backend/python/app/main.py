from flask import jsonify
from . import create_app

app = create_app()

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return jsonify({'success': False, 'error': 'A kért erőforrás nem található'}), 404

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({'success': False, 'error': 'Belső szerver hiba'}), 500

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({'success': False, 'error': 'Nem engedélyezett HTTP metódus'}), 405
