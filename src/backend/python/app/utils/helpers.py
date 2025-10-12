from ..models.database import get_db_connect


def get_difficulty_settings(difficulty):
    #Nehézségi beállítások
    settings = {
        'easy': {'time': 10, 'pairs': 3},
        'medium': {'time': 5, 'pairs': 4},
        'hard': {'time': 3, 'pairs': 6}
    }
    return settings.get(difficulty, settings['easy'])

def is_valid_game_mode(mode):
    #Játékmód validáció
    return difficulty in ['easy', 'medium', 'hard']

def is_valid_game_mode(mode):
    #Játékmód validáció
    return mode in ['color-hunter', 'card-match']

def validate_entity_exists(table, entity_id, id_field='id'):
    try:
        conn = get_db_connect()
        cursor = conn.cursor()
        cursor.execute(f"SELECT {id_field} FROM {table} WHERE {id_field} = %s", (entity_id,))
        exists = cursor.fetchone()
        cursor.close()
        conn.close()
        if not exists:
            return False, f'{table} nem található'
        return True, None
    except Exception as e:
        return False, f'Adatbázis hiba: {str(e)}'