from flask import request, jsonify, session, redirect, url_for, render_template
from ..models.user import create_or_get_player


def start_game():
    #Játék indítása a főoldalról"""
    player_name = request.form.get('player_name', '').strip()

    if not player_name:
        return redirect(url_for('index', error='Nincs név megadva'))

    session['player_name'] = player_name
    session['player_id'] = create_or_get_player(player_name)
    return redirect(url_for('game_menu'))


def select_mode():
    #Játékmód kiválasztása
    game_mode = request.form.get('game_mode', 'color-hunter')
    difficulty = request.form.get('difficulty', 'easy')

    session['game_mode'] = game_mode
    session['difficulty'] = difficulty

    if game_mode == 'color-hunter':
        return redirect(url_for('game'))
    else:
        return redirect(url_for('game2'))


def new_game():
    #Új játék indítása
    try:
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'success': False, 'error': 'Hiányzó név'}), 400

        player_name = data['name'].strip()
        if not player_name:
            return jsonify({'success': False, 'error': 'Érvénytelen név'}), 400

        player_id = create_or_get_player(player_name)
        if not player_id:
            return jsonify({'success': False, 'error': 'Hiba a játékos létrehozásakor'}), 500

        return jsonify({
            'success': True,
            'player_id': player_id,
            'player_name': player_name,
            'message': 'Játék sikeresen elindítva'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': f'Szerver hiba:{str(e)}'}), 500


# HTML Route-ok
def index():
    return render_template('main/menu/index.html')


def game_menu():
    return render_template('main/menu/gamemode-selector.html')


def game():
    return render_template('game/color-hunter/color-hunter.html')


def game2():
    return render_template('game/card-match/card-match.html')


def scores():
    return render_template('main/scoreboard/scores.html')
