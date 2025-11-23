from ..models.database import get_db_connect


def get_difficulty_settings(difficulty):
    #Nehézségi beállítások
    settings = {
        'easy': {'time': 10, 'pairs': 3},
        'medium': {'time': 5, 'pairs': 4},
        'hard': {'time': 3, 'pairs': 6}
    }
    return settings.get(difficulty, settings['easy'])

def is_valid_difficulty(difficulty):
    #Nehézségi szint validáció
    return difficulty in ['easy', 'medium', 'hard','multiplayer']

def is_valid_game_mode(mode):
    #Játékmód validáció
    return mode in ['color-hunter','color-hunter-multiplayer', 'card-match','fractal']

def validate_entity_exists(table, entity_id, id_field='id'):
    conn = None
    cursor = None
    try:
        conn = get_db_connect()
        if not conn:
            return False, 'Adatbázis kapcsolat hiba'
        cursor = conn.cursor()

        allowed_tables = ['users', 'players', 'scores', 'game_sessions']
        allowed_fields = ['id', 'username', 'player_id']
        if table not in allowed_tables or id_field not in allowed_fields:
            return False, 'Érvénytelen tábla vagy mezőnév'

        cursor.execute(f"SELECT {id_field} FROM {table} WHERE {id_field} = %s", (entity_id,))
        exists = cursor.fetchone()

        if not exists:
            return False, f'{table} nem található'
        return True, None
    except Exception as e:
        return False, f'Adatbázis hiba: {str(e)}'
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()