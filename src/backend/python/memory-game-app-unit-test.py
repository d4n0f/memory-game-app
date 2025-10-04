import unittest
from unittest.mock import Mock, patch, MagicMock
from memory_game_app import validate_score_data, get_difficulty_settings, is_valid_game_mode, get_db_connect, \
    create_or_get_player


class TestHelperFunctions(unittest.TestCase):
    """Segédfüggvények unit tesztjei"""

    def test_validate_score_data_valid(self):
        """Érvényes score adatok tesztje"""
        valid_data = {
            'player_id': '1',
            'score': '100',
            'game_mode': 'easy',
            'game_time': '120',
            'rounds_played': '5'
        }

        is_valid, error = validate_score_data(valid_data)
        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_validate_score_data_missing_field(self):
        """Hiányzó mező tesztje"""
        invalid_data = {
            'player_id': '1',
            'score': '100',
            # 'game_mode' hiányzik
            'game_time': '120',
            'rounds_played': '5'
        }

        is_valid, error = validate_score_data(invalid_data)
        self.assertFalse(is_valid)
        self.assertIn('Hiányzó mező', error)

    def test_validate_score_data_negative_score(self):
        """Negatív score tesztje"""
        invalid_data = {
            'player_id': '1',
            'score': '-50',
            'game_mode': 'easy',
            'game_time': '120',
            'rounds_played': '5'
        }

        is_valid, error = validate_score_data(invalid_data)
        self.assertFalse(is_valid)
        self.assertIn('Érvénytelen érték', error)

    def test_validate_score_data_invalid_game_mode(self):
        """Érvénytelen játékmód tesztje"""
        invalid_data = {
            'player_id': '1',
            'score': '100',
            'game_mode': 'invalid_mode',
            'game_time': '120',
            'rounds_played': '5'
        }

        is_valid, error = validate_score_data(invalid_data)
        self.assertFalse(is_valid)
        self.assertIn('Érvénytelen játékmód', error)

    def test_get_difficulty_settings(self):
        """Nehézségi beállítások tesztje"""
        easy_settings = get_difficulty_settings('easy')
        self.assertEqual(easy_settings['time'], 10)
        self.assertEqual(easy_settings['pairs'], 3)

        medium_settings = get_difficulty_settings('medium')
        self.assertEqual(medium_settings['time'], 5)
        self.assertEqual(medium_settings['pairs'], 4)

        hard_settings = get_difficulty_settings('hard')
        self.assertEqual(hard_settings['time'], 3)
        self.assertEqual(hard_settings['pairs'], 6)

        default_settings = get_difficulty_settings('invalid')
        self.assertEqual(default_settings['time'], 10)

    def test_is_valid_game_mode(self):
        """Játékmód validáció tesztje"""
        self.assertTrue(is_valid_game_mode('easy'))
        self.assertTrue(is_valid_game_mode('medium'))
        self.assertTrue(is_valid_game_mode('hard'))
        self.assertFalse(is_valid_game_mode('invalid'))
        self.assertFalse(is_valid_game_mode(''))


class TestDatabaseFunctions(unittest.TestCase):
    """Adatbázis függvények unit tesztjei"""

    @patch('memory_game_app.mysql.connector.connect')
    def test_get_db_connect_success(self, mock_connect):
        """Sikeres adatbázis kapcsolat tesztje"""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection

        result = get_db_connect()

        self.assertEqual(result, mock_connection)
        mock_connect.assert_called_once()

    @patch('memory_game_app.mysql.connector.connect')
    def test_get_db_connect_failure(self, mock_connect):
        """Sikertelen adatbázis kapcsolat tesztje"""
        mock_connect.side_effect = Exception("Connection failed")

        result = get_db_connect()

        self.assertIsNone(result)

    @patch('memory_game_app.get_db_connect')
    def test_create_or_get_player_new(self, mock_db_connect):
        """Új játékos létrehozás tesztje"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_db_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        mock_cursor.lastrowid = 123

        result = create_or_get_player("ÚjJátékos")

        self.assertEqual(result, 123)
        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called()

    @patch('memory_game_app.get_db_connect')
    def test_create_or_get_player_existing(self, mock_db_connect):
        """Létező játékos lekérés tesztje"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_db_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [456]

        result = create_or_get_player("LétezőJátékos")

        self.assertEqual(result, 456)
        update_call_found = any(
            "UPDATE players SET last_played" in str(call)
            for call in mock_cursor.execute.call_args_list
        )
        self.assertTrue(update_call_found)


class TestValidationEdgeCases(unittest.TestCase):
    """Speciális esetek validáció tesztjei"""

    def test_validate_score_data_zero_values(self):
        """Nulla értékek tesztje"""
        valid_data = {
            'player_id': '1',
            'score': '0',
            'game_mode': 'easy',
            'game_time': '0',
            'rounds_played': '1'
        }

        is_valid, error = validate_score_data(valid_data)
        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_validate_score_data_large_values(self):
        """Nagy értékek tesztje"""
        valid_data = {
            'player_id': '999999',
            'score': '999999',
            'game_mode': 'hard',
            'game_time': '999999',
            'rounds_played': '999999'
        }

        is_valid, error = validate_score_data(valid_data)
        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_validate_score_data_float_strings(self):
        """Float string értékek tesztje"""
        invalid_data = {
            'player_id': '1.5',
            'score': '100.5',
            'game_mode': 'easy',
            'game_time': '120.5',
            'rounds_played': '5.5'
        }

        is_valid, error = validate_score_data(invalid_data)
        self.assertFalse(is_valid)
        self.assertIn('Érvénytelen adatformátum', error)


class TestDifficultySettings(unittest.TestCase):
    """Nehézségi beállítások részletes tesztjei"""

    def test_difficulty_settings_structure(self):
        """Nehézségi beállítások struktúrájának tesztje"""
        for difficulty in ['easy', 'medium', 'hard']:
            settings = get_difficulty_settings(difficulty)

            self.assertIn('time', settings)
            self.assertIn('pairs', settings)
            self.assertIsInstance(settings['time'], int)
            self.assertIsInstance(settings['pairs'], int)
            self.assertGreater(settings['time'], 0)
            self.assertGreater(settings['pairs'], 0)

    def test_difficulty_progression(self):
        """Nehézségi fokozatok progressziójának tesztje"""
        easy = get_difficulty_settings('easy')
        medium = get_difficulty_settings('medium')
        hard = get_difficulty_settings('hard')

        # Idő csökken nehézség növekedésével
        self.assertGreater(easy['time'], medium['time'])
        self.assertGreater(medium['time'], hard['time'])

        # Párok száma nő nehézség növekedésével
        self.assertLess(easy['pairs'], medium['pairs'])
        self.assertLess(medium['pairs'], hard['pairs'])


if __name__ == '__main__':
    # Teszt futtatása részletes eredményekkel
    unittest.main(verbosity=2)