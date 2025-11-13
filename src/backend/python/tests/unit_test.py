import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Import path beállítása a megfelelő modulok eléréséhez
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ..app.utils.validators import (
    validate_score_data, validate_email, validate_username,
    validate_password, validate_registration_data, validate_login_data,
    validate_user_exists, validate_player_exists
)
from ..app.utils.helpers import (
    get_difficulty_settings, is_valid_difficulty,
    is_valid_game_mode, validate_entity_exists
)
from ..app.models.database import get_db_connect, init_db
from ..app.models.user import (
    get_or_create_player, create_player_for_user,
    create_guest_player, get_player_by_user_id, update_player_stats
)
from ..app.config import Config


class TestValidatorFunctions(unittest.TestCase):
    #Validátor függvények unit tesztjei

    def test_validate_email_valid(self):
        #Érvényes email cím tesztje
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org",
            "test_user123@test-domain.com"
        ]

        for email in valid_emails:
            with self.subTest(email=email):
                is_valid, error = validate_email(email, check_unique=False)
                self.assertTrue(is_valid, f"Email should be valid: {email}")
                self.assertIsNone(error)

    def test_validate_email_invalid(self):
        #Érvénytelen email cím tesztje
        invalid_emails = [
            "invalid",
            "missing@domain",
            "@missing.local",
            "spaces in@email.com",
            "missing@.com",
            "",
            None
        ]

        for email in invalid_emails:
            with self.subTest(email=email):
                is_valid, error = validate_email(email, check_unique=False)
                self.assertFalse(is_valid, f"Email should be invalid: {email}")
                self.assertIsNotNone(error)

    @patch('app.utils.validators.get_db_connect')
    def test_validate_email_unique_check(self, mock_db_connect):
        #Email egyediség ellenőrzés tesztje
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_db_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Email már létezik
        mock_cursor.fetchone.return_value = [1]
        is_valid, error = validate_email("existing@test.com", check_unique=True)
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
        
        # Email nem létezik
        mock_cursor.fetchone.return_value = None
        is_valid, error = validate_email("new@test.com", check_unique=True)
        self.assertTrue(is_valid)

    def test_validate_username_valid(self):
        #Érvényes felhasználónév tesztje
        valid_usernames = ["user123", "test_user", "User", "user_name_123", "a" * 50]

        for username in valid_usernames:
            with self.subTest(username=username):
                is_valid, error = validate_username(username, check_unique=False)
                self.assertTrue(is_valid, f"Username should be valid: {username}")
                self.assertIsNone(error)

    def test_validate_username_invalid(self):
        #Érvénytelen felhasználónév tesztje
        invalid_usernames = [
            "ab",  # Túl rövid
            "a" * 51,  # Túl hosszú
            "user@name",  # Érvénytelen karakter
            "user name",  # Szóköz
            "user-name",  # Kötőjel
            "",  # Üres
            None
        ]

        for username in invalid_usernames:
            with self.subTest(username=username):
                is_valid, error = validate_username(username, check_unique=False)
                self.assertFalse(is_valid, f"Username should be invalid: {username}")
                self.assertIsNotNone(error)

    @patch('app.utils.validators.get_db_connect')
    def test_validate_username_unique_check(self, mock_db_connect):
        #Felhasználónév egyediség ellenőrzés tesztje
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_db_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Username már létezik
        mock_cursor.fetchone.return_value = [1]
        is_valid, error = validate_username("existing_user", check_unique=True)
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)

    def test_validate_password_valid(self):
        #Érvényes jelszó tesztje
        valid_passwords = [
            "StrongPass123!",
            "MyP@ssw0rd",
            "Test1234#",
            "Complex!Password1"
        ]

        for password in valid_passwords:
            with self.subTest(password=password):
                is_valid, error = validate_password(password)
                self.assertTrue(is_valid, f"Password should be valid: {password}")
                self.assertIsNone(error)

    def test_validate_password_weak(self):
        #Gyenge jelszó tesztje
        weak_passwords = [
            ("short", "túl rövid"),
            ("nouppercase123!", "nincs nagybetű"),
            ("NOLOWERCASE123!", "nincs kisbetű"),
            ("NoNumber!", "nincs szám"),
            ("NoSpecial123", "nincs speciális karakter"),
            ("", "üres"),
            (None, "None érték")
        ]

        for pwd, description in weak_passwords:
            with self.subTest(password=pwd, description=description):
                is_valid, error = validate_password(pwd)
                self.assertFalse(is_valid, f"Password should be invalid: {description}")
                self.assertIsNotNone(error)

    def test_validate_password_strength_helper(self):
        # Jelszó erősség visszajelzés (gyenge/közepes/erős)
        from ..app.utils.validators import validate_password_strength
        self.assertEqual(validate_password_strength('short'), 'gyenge')
        self.assertIn(validate_password_strength('abcdEF12'), ['közepes','erős'])
        self.assertEqual(validate_password_strength('Abcdef12!'), 'erős')

    @patch('app.utils.validators.validate_username')
    @patch('app.utils.validators.validate_email')
    @patch('app.utils.validators.validate_password')
    def test_validate_registration_data_valid(self, mock_pass, mock_email, mock_user):

        #Érvényes regisztrációs adatok tesztje
        mock_user.return_value = (True, None)
        mock_email.return_value = (True, None)
        mock_pass.return_value = (True, None)

        valid_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPassword123!'
        }

        is_valid, error = validate_registration_data(valid_data)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
        mock_user.assert_called_once()
        mock_email.assert_called_once()
        mock_pass.assert_called_once()

    def test_validate_registration_data_missing_fields(self):
        #Hiányzó mezők tesztje regisztrációnál
        incomplete_data = [
            {'email': 'test@example.com', 'password': 'Test123!'},
            {'username': 'testuser', 'password': 'Test123!'},
            {'username': 'testuser', 'email': 'test@example.com'},
            {}
        ]

        for data in incomplete_data:
            with self.subTest(data=data):
                is_valid, error = validate_registration_data(data)
                self.assertFalse(is_valid)
                self.assertIsNotNone(error)

    def test_validate_login_data_valid(self):
        #Érvényes bejelentkezési adatok tesztje
        valid_data = {
            'username': 'testuser',
            'password': 'password123'
        }

        is_valid, error = validate_login_data(valid_data)
        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_validate_login_data_missing_fields(self):
        #Hiányzó mezők tesztje bejelentkezésnél
        incomplete_data = [
            {'username': 'testuser'},
            {'password': 'password123'},
            {}
        ]

        for data in incomplete_data:
            with self.subTest(data=data):
                is_valid, error = validate_login_data(data)
                self.assertFalse(is_valid)
                self.assertIsNotNone(error)

    @patch('app.utils.validators.validate_entity_exists')
    def test_validate_score_data_valid(self, mock_validate):
        #Érvényes score adatok tesztje
        valid_data = {
            'player_id': 1,
            'score': 100,
            'game_mode': 'color-hunter',
            'game_time': 60,
            'rounds_played': 5,
            'difficulty': 'easy'
        }

        is_valid, error = validate_score_data(valid_data)
        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_validate_score_data_missing_fields(self):
        #Hiányzó mezők tesztje score adatoknál
        incomplete_data = [
            {'score': 100, 'game_mode': 'color-hunter', 'rounds_played': 1},
            {'player_id': 1, 'game_mode': 'color-hunter', 'rounds_played': 1},
            {'player_id': 1, 'score': 100, 'rounds_played': 1},
            {'player_id': 1, 'score': 100, 'game_mode': 'color-hunter'}
        ]

        for data in incomplete_data:
            with self.subTest(data=data):
                is_valid, error = validate_score_data(data)
                self.assertFalse(is_valid)
                self.assertIsNotNone(error)

    def test_validate_score_data_invalid_values(self):
        #Érvénytelen értékek tesztje score adatoknál
        invalid_data = [
            {'player_id': 1, 'score': -1, 'game_mode': 'color-hunter', 'rounds_played': 1, 'game_time': 0},
            {'player_id': 1, 'score': 100, 'game_mode': 'color-hunter', 'rounds_played': 0, 'game_time': 0},
            {'player_id': 1, 'score': 100, 'game_mode': 'color-hunter', 'rounds_played': 1, 'game_time': -1},
            {'player_id': 1, 'score': 100, 'game_mode': 'invalid-mode', 'rounds_played': 1, 'game_time': 0},
            {'player_id': 1, 'score': 100, 'game_mode': 'color-hunter', 'rounds_played': 1, 'game_time': 0, 'difficulty': 'invalid'}
        ]

        for data in invalid_data:
            with self.subTest(data=data):
                is_valid, error = validate_score_data(data)
                self.assertFalse(is_valid)
                self.assertIsNotNone(error)


class TestHelperFunctions(unittest.TestCase):
    #Segédfüggvények unit tesztjei

    def test_get_difficulty_settings(self):
        #Nehézségi beállítások tesztje
        difficulties = ['easy', 'medium', 'hard']
        expected_times = [10, 5, 3]
        expected_pairs = [3, 4, 6]

        for i, diff in enumerate(difficulties):
            with self.subTest(difficulty=diff):
                settings = get_difficulty_settings(diff)
                self.assertEqual(settings['time'], expected_times[i])
                self.assertEqual(settings['pairs'], expected_pairs[i])

        # Alapértelmezett érték
        default_settings = get_difficulty_settings('invalid')
        self.assertEqual(default_settings['time'], 10)
        self.assertEqual(default_settings['pairs'], 3)

    def test_is_valid_difficulty(self):
        #Nehézségi szint validáció tesztje
        self.assertTrue(is_valid_difficulty('easy'))
        self.assertTrue(is_valid_difficulty('medium'))
        self.assertTrue(is_valid_difficulty('hard'))
        self.assertFalse(is_valid_difficulty('invalid'))
        self.assertFalse(is_valid_difficulty(''))
        self.assertFalse(is_valid_difficulty(None))

    def test_is_valid_game_mode(self):
        #Játékmód validáció tesztje
        self.assertTrue(is_valid_game_mode('color-hunter'))
        self.assertTrue(is_valid_game_mode('card-match'))
        self.assertFalse(is_valid_game_mode('invalid-mode'))
        self.assertFalse(is_valid_game_mode(''))
        self.assertFalse(is_valid_game_mode(None))

    @patch('app.utils.helpers.get_db_connect')
    def test_validate_entity_exists_success(self, mock_db_connect):
        #Entitás létezés validáció sikeres tesztje
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_db_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.is_connected.return_value = True

        # Entitás létezik
        mock_cursor.fetchone.return_value = [1]
        exists, error = validate_entity_exists('players', 1)
        self.assertTrue(exists)
        self.assertIsNone(error)
        mock_cursor.close.assert_called()
        mock_conn.close.assert_called()

    @patch('app.utils.helpers.get_db_connect')
    def test_validate_entity_exists_not_found(self, mock_db_connect):
        #Entitás nem létezik tesztje
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_db_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.is_connected.return_value = True

        mock_cursor.fetchone.return_value = None
        exists, error = validate_entity_exists('players', 999)
        self.assertFalse(exists)
        self.assertIsNotNone(error)

    @patch('app.utils.helpers.get_db_connect')
    def test_validate_entity_exists_invalid_table(self, mock_db_connect):
        #Érvénytelen tábla név tesztje
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_db_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.is_connected.return_value = True

        exists, error = validate_entity_exists('invalid_table', 1)
        self.assertFalse(exists)
        self.assertIsNotNone(error)

    @patch('app.utils.helpers.get_db_connect')
    def test_validate_entity_exists_no_connection(self, mock_db_connect):
        #Nincs adatbázis kapcsolat tesztje
        mock_db_connect.return_value = None
        
        exists, error = validate_entity_exists('players', 1)
        self.assertFalse(exists)
        self.assertIsNotNone(error)


class TestUserModelFunctions(unittest.TestCase):
    #User model függvények unit tesztjei

    @patch('app.models.user.get_db_connect')
    def test_create_player_for_user_success(self, mock_db_connect):
        #Sikeres játékos létrehozás felhasználóhoz
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_db_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.is_connected.return_value = True
        mock_cursor.lastrowid = 123

        player_id = create_player_for_user(1, "testuser")
        self.assertEqual(player_id, 123)
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called()
        mock_conn.close.assert_called()

    @patch('app.models.user.get_db_connect')
    def test_create_player_for_user_failure_no_connection(self, mock_db_connect):
        #Sikertelen játékos létrehozás - nincs kapcsolat
        mock_db_connect.return_value = None
        player_id = create_player_for_user(1, "testuser")
        self.assertIsNone(player_id)

    @patch('app.models.user.get_db_connect')
    def test_create_player_for_user_failure_exception(self, mock_db_connect):
        #Sikertelen játékos létrehozás - exception
        from mysql.connector import Error
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_db_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.is_connected.return_value = True
        mock_cursor.execute.side_effect = Error("Database error")

        player_id = create_player_for_user(1, "testuser")
        self.assertIsNone(player_id)

    @patch('app.models.user.get_db_connect')
    def test_create_guest_player_success(self, mock_db_connect):
        #Sikeres vendég játékos létrehozás
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_db_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.is_connected.return_value = True
        mock_cursor.lastrowid = 456

        player_id = create_guest_player("guestplayer")
        self.assertEqual(player_id, 456)
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    @patch('app.models.user.get_db_connect')
    def test_get_or_create_player_existing(self, mock_db_connect):
        #Létező játékos lekérése
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_db_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.is_connected.return_value = True
        mock_cursor.fetchone.return_value = [789]

        player_id = get_or_create_player("existingplayer")
        self.assertEqual(player_id, 789)
        mock_conn.commit.assert_called()

    @patch('app.models.user.create_guest_player')
    @patch('app.models.user.get_db_connect')
    def test_get_or_create_player_new_guest(self, mock_db_connect, mock_guest):
        #Új vendég játékos létrehozása
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_db_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.is_connected.return_value = True
        mock_cursor.fetchone.return_value = None
        mock_guest.return_value = 999

        player_id = get_or_create_player("newguest", user_id=None)
        self.assertEqual(player_id, 999)
        mock_guest.assert_called_once_with("newguest")

    @patch('app.models.user.create_player_for_user')
    @patch('app.models.user.get_db_connect')
    def test_get_or_create_player_new_user(self, mock_db_connect, mock_create):
        #Új játékos létrehozása user_id-vel
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_db_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.is_connected.return_value = True
        mock_cursor.fetchone.return_value = None
        mock_create.return_value = 888

        player_id = get_or_create_player("newuser", user_id=1)
        self.assertEqual(player_id, 888)
        mock_create.assert_called_once_with(1, "newuser")

    @patch('app.models.user.get_db_connect')
    def test_get_player_by_user_id_success(self, mock_db_connect):
        #Player lekérése user_id alapján
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_db_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.is_connected.return_value = True
        mock_cursor.fetchone.return_value = {'id': 1, 'display_name': 'test'}

        player = get_player_by_user_id(1)
        self.assertIsNotNone(player)
        self.assertEqual(player['id'], 1)

    @patch('app.models.user.get_db_connect')
    def test_get_player_by_user_id_not_found(self, mock_db_connect):
        #Player nem található
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_db_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.is_connected.return_value = True
        mock_cursor.fetchone.return_value = None

        player = get_player_by_user_id(999)
        self.assertIsNone(player)

    @patch('app.models.user.get_db_connect')
    def test_update_player_stats_success(self, mock_db_connect):
        #Player statisztikák frissítése
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_db_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.is_connected.return_value = True

        result = update_player_stats(1, 1500)
        self.assertTrue(result)
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    @patch('app.models.user.get_db_connect')
    def test_update_player_stats_failure(self, mock_db_connect):
        #Player statisztikák frissítése sikertelen
        from mysql.connector import Error
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_db_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.is_connected.return_value = True
        mock_cursor.execute.side_effect = Error("Database error")

        result = update_player_stats(1, 1500)
        self.assertFalse(result)


class TestDatabaseFunctions(unittest.TestCase):
    #Adatbázis függvények unit tesztjei

    @patch('app.models.database.mysql.connector.connect')
    def test_get_db_connect_success(self, mock_connect):
        #Sikeres adatbázis kapcsolat
        mock_connection = Mock()
        mock_connect.return_value = mock_connection

        result = get_db_connect()
        self.assertEqual(result, mock_connection)

    @patch('app.models.database.mysql.connector.connect')
    def test_get_db_connect_failure(self, mock_connect):
        #Sikertelen adatbázis kapcsolat
        from mysql.connector import Error
        mock_connect.side_effect = Error("Connection failed")
        
        result = get_db_connect()
        self.assertIsNone(result)


class TestEdgeCases(unittest.TestCase):
    #Speciális esetek és edge case-ek tesztjei

    def test_validate_score_data_edge_cases(self):
        #Score adatok edge case tesztjei
        test_cases = [
            ({'player_id': 1, 'score': 0, 'game_mode': 'color-hunter', 'game_time': 0, 'rounds_played': 1},
             True, "Zero values"),
            ({'player_id': 1, 'score': 999999, 'game_mode': 'card-match', 'game_time': 999999,
              'rounds_played': 999999}, True, "Large values"),
            ({'player_id': 1, 'score': 100, 'game_mode': 'color-hunter', 'rounds_played': 1}, 
             True, "Missing optional game_time"),
        ]

        for data, should_be_valid, description in test_cases:
            with self.subTest(description=description):
                is_valid, error = validate_score_data(data)
                if should_be_valid:
                    self.assertTrue(is_valid, f"Should be valid: {description}. Error: {error}")
                else:
                    self.assertFalse(is_valid, f"Should be invalid: {description}")

    def test_validate_username_edge_cases(self):
        #Felhasználónév edge case tesztjei
        edge_cases = [
            ("a" * 50, True, "Maximum length"),
            ("a" * 51, False, "Over maximum length"),
            ("_user", True, "Starts with underscore"),
            ("user_", True, "Ends with underscore"),
            ("1user", True, "Starts with number"),
            ("USER123", True, "All uppercase"),
        ]

        for username, should_be_valid, description in edge_cases:
            with self.subTest(description=description):
                is_valid, error = validate_username(username, check_unique=False)
                self.assertEqual(is_valid, should_be_valid,
                                 f"{description}: {username} -> valid={is_valid}, error={error}")

    def test_validate_password_edge_cases(self):
        #Jelszó edge case tesztjei
        edge_cases = [
            ("A" * 7 + "1!", False, "Exactly 7 chars (too short)"),
            ("A" * 8 + "1!", True, "Exactly 8 chars (minimum)"),
            ("a" * 8 + "A1!", True, "Mixed case, numbers, special"),
        ]

        for password, should_be_valid, description in edge_cases:
            with self.subTest(description=description):
                is_valid, error = validate_password(password)
                self.assertEqual(is_valid, should_be_valid,
                                 f"{description}: valid={is_valid}, error={error}")


def run_unit_tests():
    #Unit tesztek futtatása részletes eredményekkel
    print("UNIT TESZTEK INDÍTÁSA...")
    print("=" * 60)

    # Teszt loader létrehozása
    loader = unittest.TestLoader()

    # Összes teszt betöltése
    test_suites = [
        loader.loadTestsFromTestCase(TestValidatorFunctions),
        loader.loadTestsFromTestCase(TestHelperFunctions),
        loader.loadTestsFromTestCase(TestUserModelFunctions),
        loader.loadTestsFromTestCase(TestDatabaseFunctions),
        loader.loadTestsFromTestCase(TestEdgeCases)
    ]

    # Összes teszt egy suite-ban
    all_tests = unittest.TestSuite(test_suites)

    # Teszt futtató
    runner = unittest.TextTestRunner(verbosity=2, descriptions=True)
    result = runner.run(all_tests)

    # Eredmény összefoglaló
    print("=" * 60)
    print("UNIT TESZT EREDMÉNYEK:")
    print(f"Sikeres: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Sikertelen: {len(result.failures)}")
    print(f"Hibák: {len(result.errors)}")
    print(f"Összes teszt: {result.testsRun}")

    if result.failures:
        print("\nSIKERTELEN TESZTEK:")
        for test, traceback in result.failures:
            print(f"\n{test}")
            print(traceback)

    if result.errors:
        print("\nHIBÁK:")
        for test, traceback in result.errors:
            print(f"\n{test}")
            print(traceback)

    if result.wasSuccessful():
        print("\n✅ ÖSSZES UNIT TESZT SIKERES!")
    else:
        print("\n❌ NÉHÁNY UNIT TESZT SIKERTELEN")

    return result.wasSuccessful()


if __name__ == '__main__':
    run_unit_tests()