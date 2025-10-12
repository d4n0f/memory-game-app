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
from ..app.models.database import (get_db_connect,init_db)
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
            "user+tag@example.org"
        ]

        for email in valid_emails:
            with self.subTest(email=email):
                is_valid, error = validate_email(email)
                self.assertTrue(is_valid)
                self.assertIsNone(error)

    def test_validate_email_invalid(self):
        #Érvénytelen email cím tesztje
        invalid_emails = [
            "invalid",
            "missing@domain",
            "@missing.local",
            "spaces in@email.com"
        ]

        for email in invalid_emails:
            with self.subTest(email=email):
                is_valid, error = validate_email(email)
                self.assertFalse(is_valid)
                self.assertIsNotNone(error)

    def test_validate_username_valid(self):
        #Érvényes felhasználónév tesztje
        valid_usernames = ["user123", "test_user", "User", "user_name_123"]

        for username in valid_usernames:
            with self.subTest(username=username):
                is_valid, error = validate_username(username)
                self.assertTrue(is_valid)
                self.assertIsNone(error)

    def test_validate_username_invalid(self):
        #Érvénytelen felhasználónév tesztje
        invalid_usernames = [
            "ab",  # Túl rövid
            "a" * 51,  # Túl hosszú
            "user@name",  # Érvénytelen karakter
            "user name",  # Szóköz
            ""  # Üres
        ]

        for username in invalid_usernames:
            with self.subTest(username=username):
                is_valid, error = validate_username(username)
                self.assertFalse(is_valid)
                self.assertIsNotNone(error)

    def test_validate_password_valid(self):
        #Érvényes jelszó tesztje
        valid_password = "StrongPass123!"
        is_valid, error = validate_password(valid_password, valid_password)
        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_validate_password_weak(self):
        #Gyenge jelszó tesztje
        weak_passwords = [
            "short",  # Túl rövid
            "nouppercase123!",  # Nincs nagybetű
            "NOLOWERCASE123!",  # Nincs kisbetű
            "NoNumber!",  # Nincs szám
            "NoSpecial123"  # Nincs speciális karakter
        ]

        for pwd in weak_passwords:
            with self.subTest(password=pwd):
                is_valid, error = validate_password(pwd, pwd)
                self.assertFalse(is_valid)
                self.assertIsNotNone(error)

    def test_validate_password_mismatch(self):
        #Nem egyező jelszavak tesztje
        is_valid, error = validate_password("Password123!", "Different123!")
        self.assertFalse(is_valid)
        self.assertIn("nem egyeznek", error.lower())

    def test_validate_registration_data_valid(self):
        #Érvényes regisztrációs adatok tesztje
        valid_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPassword123!',
            'confirm_password': 'TestPassword123!'
        }

        with patch('app.utils.validators.validate_username') as mock_user, \
                patch('app.utils.validators.validate_email') as mock_email, \
                patch('app.utils.validators.validate_password') as mock_pass:
            mock_user.return_value = (True, None)
            mock_email.return_value = (True, None)
            mock_pass.return_value = (True, None)

            is_valid, error = validate_registration_data(valid_data)
            self.assertTrue(is_valid)
            self.assertIsNone(error)

    def test_validate_registration_data_missing_fields(self):
        #Hiányzó mezők tesztje regisztrációnál
        incomplete_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            # 'password' hiányzik
            # 'confirm_password' hiányzik
        }

        is_valid, error = validate_registration_data(incomplete_data)
        self.assertFalse(is_valid)
        self.assertIn("hiányzó", error.lower())

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
        incomplete_data = {
            'username': 'testuser'
            # 'password' hiányzik
        }

        is_valid, error = validate_login_data(incomplete_data)
        self.assertFalse(is_valid)
        self.assertIn("jelszó", error.lower())


class TestHelperFunctions(unittest.TestCase):
    #Segédfüggvények unit tesztjei

    def test_get_difficulty_settings(self):
        #Nehézségi beállítások tesztje
        # Érvényes nehézségi szintek
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
    def test_validate_entity_exists(self, mock_db_connect):
        #Entitás létezés validáció tesztje
        # Mock adatbázis kapcsolat
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_db_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Teszt: entitás létezik
        mock_cursor.fetchone.return_value = [1]
        exists, error = validate_entity_exists('players', 1)
        self.assertTrue(exists)
        self.assertIsNone(error)

        # Teszt: entitás nem létezik
        mock_cursor.fetchone.return_value = None
        exists, error = validate_entity_exists('players', 999)
        self.assertFalse(exists)
        self.assertIsNotNone(error)


class TestUserModelFunctions(unittest.TestCase):
    #User model függvények unit tesztjei

    @patch('app.models.user.get_db_connect')
    def test_create_player_for_user_success(self, mock_db_connect):
        #Sikeres játékos létrehozás felhasználóhoz#
        # Mock adatbázis
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_db_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 123

        # Teszt
        player_id = create_player_for_user(1, "testuser")
        self.assertEqual(player_id, 123)

    @patch('app.models.user.get_db_connect')
    def test_create_player_for_user_failure(self, mock_db_connect):
        #Sikertelen játékos létrehozás
        mock_db_connect.return_value = None
        player_id = create_player_for_user(1, "testuser")
        self.assertIsNone(player_id)

    @patch('app.models.user.get_db_connect')
    def test_create_guest_player_success(self, mock_db_connect):
        #Sikeres vendég játékos létrehozás
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_db_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 456

        player_id = create_guest_player("guestplayer")
        self.assertEqual(player_id, 456)

    @patch('app.models.user.get_db_connect')
    def test_get_or_create_player_existing(self, mock_db_connect):
        #Létező játékos lekérése
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_db_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [789]  # Létező player ID

        player_id = get_or_create_player("existingplayer")
        self.assertEqual(player_id, 789)

    @patch('app.models.user.get_db_connect')
    def test_get_or_create_player_new_guest(self, mock_db_connect):
        #Új vendég játékos létrehozása
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_db_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None  # Nem létezik

        # Mock create_guest_player-t
        with patch('app.models.user.create_guest_player') as mock_guest:
            mock_guest.return_value = 999
            player_id = get_or_create_player("newguest", user_id=None)
            self.assertEqual(player_id, 999)

    @patch('app.models.user.get_db_connect')
    def test_update_player_stats_success(self, mock_db_connect):
        #Player statisztikák frissítése
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_db_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        result = update_player_stats(1, 1500)
        self.assertTrue(result)


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
        mock_connect.side_effect = Exception("Connection failed")
        result = get_db_connect()
        self.assertIsNone(result)


class TestEdgeCases(unittest.TestCase):
    #Speciális esetek és edge case-ek tesztjei

    def test_validate_score_data_edge_cases(self):
        #Score adatok edge case tesztjei
        # Mock függvények, ha szükséges
        with patch('app.utils.validators.validate_player_exists') as mock_player:
            mock_player.return_value = (True, None)

            test_cases = [
                ({'player_id': 1, 'score': 0, 'game_mode': 'color-hunter', 'game_time': 0, 'rounds_played': 1},
                 True, "Zero values"),
                ({'player_id': 1, 'score': 999999, 'game_mode': 'card-match', 'game_time': 999999,
                  'rounds_played': 999999}, True, "Large values"),
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
        ]

        for username, should_be_valid, description in edge_cases:
            with self.subTest(description=description):
                is_valid, error = validate_username(username)
                self.assertEqual(is_valid, should_be_valid,
                                 f"{description}: {username} -> valid={is_valid}, error={error}")


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

    if result.wasSuccessful():
        print("ÖSSZES UNIT TESZT SIKERES!")
    else:
        print("NÉHÁNY UNIT TESZT SIKERTELEN")

    return result.wasSuccessful()


if __name__ == '__main__':
    run_unit_tests()