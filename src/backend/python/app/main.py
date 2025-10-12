from flask import Flask, jsonify
from .config import Config
from datetime import datetime

# Route importok
from .routes.game import (
    index, game_menu, game, game2, scores,
    start_game, select_mode, new_game, end_game_session, get_game_session
)
from .routes.scores import save_scores, get_scores, get_players
from .routes.static import serve_css, serve_js, serve_color_match_images, serve_general_images
from .routes.auth import register_user, login_user, logout_user, get_current_user

app = Flask(__name__, static_folder=Config.FRONTEND_DIR,
    template_folder=Config.FRONTEND_DIR)
app.secret_key = 'your-secret-key-here'  # Fontos a session-hoz!


# Route-ok beállítása
# HTML Route-ok
app.route('/')(index)
app.route('/menu')(game_menu)
app.route('/color-hunter')(game)
app.route('/card-match')(game2)
app.route('/scores')(scores)


# Form Route-ok
app.route('/start-game', methods=['POST'])(start_game)
app.route('/select-mode', methods=['POST'])(select_mode)

# AUTH Route-ok - ÚJ
app.route('/api/register', methods=['POST'])(register_user)
app.route('/api/login', methods=['POST'])(login_user)
app.route('/api/logout', methods=['POST'])(logout_user)
app.route('/api/current-user', methods=['GET'])(get_current_user)

# GAME API Route-ok - BŐVÍTETT
app.route('/api/health')(lambda: jsonify({'status': 'ok', 'database': 'Csatlakozott', 'time': datetime.now().isoformat()}))
app.route('/api/game', methods=['POST'])(new_game)
app.route('/api/game/session/end', methods=['POST'])(end_game_session)
app.route('/api/game/session', methods=['GET'])(get_game_session)

# SCORES API Route-ok
app.route('/api/save', methods=['POST'])(save_scores)
app.route('/api/scores', methods=['GET'])(get_scores)
app.route('/api/players', methods=['GET'])(get_players)


# Static file Route-ok
app.route('/styles/<path:filename>')(serve_css)
app.route('/scripts/<path:filename>')(serve_js)
app.route('/assets/images/color-match/<path:filename>')(serve_color_match_images)
app.route('/assets/images/<path:filename>')(serve_general_images)

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
