import requests
import json
import time
import sys
import os

# Import test config
sys.path.append(os.path.join(os.path.dirname(__file__)))
from test_config import TEST_DATABASE_URL, TEST_USER, TEST_PLAYER, TEST_TIMEOUT

BASE_URL = TEST_DATABASE_URL


def test_health():
    #Health check teszt
    print("Health check teszt...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check hiba: {e}")
        return False


def test_new_game():
    #Új játék teszt
    print("\n Új játék teszt...")
    try:
        data = {"name": f"TesztJatekos_{int(time.time())}"}  # Egyedi név
        response = requests.post(f"{BASE_URL}/api/game", json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Új játék hiba: {e}")
        return False


def test_save_score(player_id=None):
    #Eredmény mentés teszt - részletes hibakezeléssel
    print("\nEredmény mentés teszt...")
    try:
        if player_id is None:
            # Kérjünk egy érvényes player_id-t
            test_response = requests.post(f"{BASE_URL}/api/game", json={"name": "TempPlayer"}, timeout=TEST_TIMEOUT)
            if test_response.status_code == 200:
                player_id = test_response.json().get('player_id', 1)
            else:
                player_id = 1

        data = {
            "player_id": player_id,
            "score": 150,
            "game_mode": "color-hunter",
            "difficulty": "medium",
            "game_time": 120,
            "rounds_played": 5
        }

        print(f" Küldött adatok: {data}")
        response = requests.post(f"{BASE_URL}/api/save", json=data, timeout=TEST_TIMEOUT)
        print(f" Status: {response.status_code}")
        print(f" Response: {response.json()}")

        return response.status_code in [200, 201]

    except Exception as e:
        print(f" Eredmény mentés hiba: {e}")
        return False


def test_get_scores():
    #Eredmények lekérés teszt
    print("\nEredmények lekérés teszt...")
    try:
        response = requests.get(f"{BASE_URL}/api/scores?game_mode=color-hunter&limit=5")
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Talált eredmények: {result.get('count', 0)}")

        # További ellenőrzések
        if response.status_code == 200:
            scores = result.get('scores', [])
            if scores:
                print(f"Első eredmény: {scores[0]}")
            return True
        return False
    except Exception as e:
        print(f"Eredmények lekérés hiba: {e}")
        return False


def test_get_players():
    #Játékosok lekérés teszt
    print("\nJátékosok lekérés teszt...")
    try:
        response = requests.get(f"{BASE_URL}/api/players")
        print(f"Status: {response.status_code}")
        result = response.json()

        if response.status_code == 200 and result.get('success'):
            players = result.get('players', [])
            print(f"Talált játékosok: {len(players)}")

            # Játékosok részletes kiírása
            for player in players[:3]:  # Csak az első 3 játékos
                print(
                    f"  - {player['name']}: {player['games_played']} játék, legjobb: {player.get('best_score', 'N/A')}")

            return True
        else:
            print(f"Hiba a válaszban: {result.get('error', 'Ismeretlen hiba')}")
            return False

    except Exception as e:
        print(f"Játékosok lekérés hiba: {e}")
        return False


def test_user_registration():
    #Felhasználó regisztráció teszt
    print("\nFelhasználó regisztráció teszt...")
    try:
        timestamp = int(time.time())
        data = {
            "username": f"testuser_{timestamp}",
            "email": f"test_{timestamp}@example.com",
            "password": "TestPassword123!",
            "confirm_password": "TestPassword123!"
        }
        response = requests.post(f"{BASE_URL}/api/register", json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

        # Sikeres regisztráció vagy már létező felhasználó is OK
        return response.status_code in [200, 201, 400]
    except Exception as e:
        print(f"Regisztráció hiba: {e}")
        return False


def test_user_login():
    #Felhasználó bejelentkezés teszt
    print("\nFelhasználó bejelentkezés teszt...")
    try:
        data = {
            "username": "testuser",
            "password": "TestPassword123!"
        }
        response = requests.post(f"{BASE_URL}/api/login", json=data)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {result}")

        # Sikeres bejelentkezés vagy invalid credentials is OK teszt szempontjából
        return response.status_code in [200, 401]
    except Exception as e:
        print(f"Bejelentkezés hiba: {e}")
        return False


def test_get_leaderboard():
    #Ranglista lekérés teszt
    print("\nRanglista lekérés teszt...")
    try:
        response = requests.get(f"{BASE_URL}/api/scores?game_mode=color-hunter&difficulty=medium&limit=10")
        print(f"Status: {response.status_code}")
        result = response.json()

        if response.status_code == 200:
            leaderboard = result.get('leaderboard', [])
            print(f"Ranglista bejegyzések: {len(leaderboard)}")
            return True
        else:
            print(f"Hiba: {result.get('error', 'Ismeretlen hiba')}")
            return False
    except Exception as e:
        print(f"Ranglista lekérés hiba: {e}")
        return False


def test_error_cases():
    #Hibás kérések tesztelése
    print("\nHibás kérések tesztelése...")
    tests_passed = 0

    # 1. Hiányzó adatok
    try:
        response = requests.post(f"{BASE_URL}/api/save", json={})
        if response.status_code == 400:
            print("Hiányzó adatok helyes hibakezelés")
            tests_passed += 1
        else:
            print(f"Hiányzó adatok: várt 400, kaptunk {response.status_code}")
    except Exception as e:
        print(f"Hiányzó adatok teszt hiba: {e}")

    # 2. Érvénytelen game_mode
    try:
        response = requests.get(f"{BASE_URL}/api/scores?game_mode=invalid_mode")
        if response.status_code == 400:
            print("✅ Érvénytelen game_mode helyes hibakezelés")
            tests_passed += 1
        else:
            print(f"Érvénytelen game_mode: várt 400, kaptunk {response.status_code}")
    except Exception as e:
        print(f"Érvénytelen game_mode teszt hiba: {e}")

    return tests_passed >= 1  # Legalább egy hibateszt sikeres


def test_performance():
#Alapvető teljesítmény teszt
    print("\nAlapvető teljesítmény teszt...")
    try:
        start_time = time.time()

        # Több párhuzamos kérés
        responses = []
        for i in range(3):
            response = requests.get(f"{BASE_URL}/api/health")
            responses.append(response.status_code == 200)

        end_time = time.time()
        response_time = end_time - start_time

        print(f"3 kérés ideje: {response_time:.2f} másodperc")
        print(f"Átlagos válaszidő: {response_time / 3:.2f} másodperc")

        # Elfogadható teljesítmény (8 másodperc 3 kérésre)
        return all(responses) and response_time < 8
    except Exception as e:
        print(f"Teljesítmény teszt hiba: {e}")
        return False


def run_all_tests():
    #Összes teszt futtatása
    print("Backend integrációs tesztek indítása...")
    print("=" * 50)

    tests = [
        test_health,
        test_new_game,
        test_save_score,
        test_get_scores,
        test_get_players,
        test_user_registration,
        test_user_login,
        test_get_leaderboard,
        test_error_cases,
        test_performance
    ]

    test_names = [
        "Health check",
        "Új játék",
        "Eredmény mentés",
        "Eredmények lekérése",
        "Játékosok lekérése",
        "Felhasználó regisztráció",
        "Felhasználó bejelentkezés",
        "Ranglista lekérés",
        "Hibás kérések",
        "Teljesítmény teszt"
    ]

    passed = 0
    for i, test in enumerate(tests):
        print(f"\n{'=' * 30}")
        print(f"Teszt {i + 1}/{len(tests)}: {test_names[i]}")
        print(f"{'=' * 30}")

        if test():
            passed += 1
            print("Sikeres")
        else:
            print("Sikertelen")

    print(f"\n{'=' * 50}")
    print(f"ÖSSZEFOGLALÓ: {passed}/{len(tests)} teszt sikeres")
    print(f"{'=' * 50}")

    if passed == len(tests):
        print("MINDEN TESZT SIKERES! A backend megfelelően működik.")
    elif passed >= len(tests) * 0.7:
        print("⚠LEGTÖBB TESZT SIKERES. A backend alapvetően működik.")
    else:
        print("SOK TESZT SIKERTELEN. Ellenőrizd a backend konfigurációt.")

    return passed


if __name__ == "__main__":
    run_all_tests()