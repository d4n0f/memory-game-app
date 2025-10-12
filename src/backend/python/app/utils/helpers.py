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
    return mode in ['easy', 'medium', 'hard']