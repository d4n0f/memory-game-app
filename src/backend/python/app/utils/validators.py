def validate_score_data(data):
    #Score adatok validálása
    required_fields = ['player_id', 'score', 'game_mode', 'game_time', 'rounds_played']

    for field in required_fields:
        if field not in data:
            return False, f'Hiányzó mező: {field}'

    try:
        player_id = int(data['player_id'])
        score = int(data['score'])
        game_time = int(data.get('game_time', 0))
        rounds_played = int(data.get('rounds_played', 1))

        if score < 0 or game_time < 0 or rounds_played < 1:
            return False, 'Érvénytelen érték'

        if data['difficulty'] not in ['easy', 'medium', 'hard']:
            return False, 'Érvénytelen játékmód'

        return True, None

    except (ValueError, TypeError):
        return False, 'Érvénytelen adatformátum'