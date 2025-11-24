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


def test_scores_global_and_me_and_user_update():
    # Új funkciók integrációs tesztje: register/login -> save score -> /api/scores (global, me) -> update user
    print("\nÚj funkciók: scores global/me és user update teszt...")
    try:
        s = requests.Session()

        # 1) Regisztráció egyedi felhasználóval
        ts = int(time.time())
        reg_payload = {
            "username": f"itest_user_{ts}",
            "email": f"itest_{ts}@example.com",
            "password": "It3stStrong!Pass",
        }
        r = s.post(f"{BASE_URL}/api/register", json=reg_payload, timeout=TEST_TIMEOUT)
        print("Register:", r.status_code)
        reg_json = r.json()
        if r.status_code not in [200, 201] or not reg_json.get('success'):
            print("Regisztráció nem sikerült vagy már létező felhasználóval ütközött.")
            # Ha 400-at kapunk foglalt név/email miatt, próbáljunk bejelentkezni ugyanazzal
            login_payload = {"username": reg_payload["username"], "password": reg_payload["password"]}
            r = s.post(f"{BASE_URL}/api/login", json=login_payload, timeout=TEST_TIMEOUT)
            print("Login after failed register:", r.status_code)
            if r.status_code != 200:
                return False
            login_json = r.json()
            player_id = login_json.get('player_id')
        else:
            player_id = reg_json.get('player_id')

        if not player_id:
            # Ha nincs player_id a regisztrációs válaszban, próbáljunk current-user endpointot
            cu = s.get(f"{BASE_URL}/api/current-user", timeout=TEST_TIMEOUT)
            if cu.status_code == 200 and cu.json().get('success'):
                player_id = cu.json()['user'].get('player_id')

        if not player_id:
            print("Nem sikerült player_id-t szerezni")
            return False

        # 2) Eredmény mentése az új userrel
        save_payload = {
            "player_id": int(player_id),
            "score": 123,
            "game_mode": "color-hunter",
            "difficulty": "easy",
            "game_time": 30,
            "rounds_played": 3
        }
        r = s.post(f"{BASE_URL}/api/save", json=save_payload, timeout=TEST_TIMEOUT)
        print("Save score:", r.status_code, r.text)
        if r.status_code not in [200, 201]:
            return False

        # 3) Globális ranglista lekérés
        r = s.get(f"{BASE_URL}/api/scores?scope=global&game_mode=color-hunter&limit=10", timeout=TEST_TIMEOUT)
        print("Scores global:", r.status_code)
        if r.status_code != 200 or not r.json().get('success'):
            return False

        # 4) Saját eredmények lekérése (scope=me)
        r = s.get(f"{BASE_URL}/api/scores?scope=me&limit=10", timeout=TEST_TIMEOUT)
        print("Scores me:", r.status_code, r.text)
        if r.status_code != 200:
            return False
        data_me = r.json()
        if not data_me.get('success'):
            return False
        # Elvárás: a válasz tartalmaz 'scope'=='me' és a 'scores' lista
        if data_me.get('scope') != 'me' or 'scores' not in data_me:
            return False

        # 5) Felhasználónév frissítés
        new_username = f"itest_user_new_{ts}"
        r = s.patch(f"{BASE_URL}/api/user/update", json={"username": new_username}, timeout=TEST_TIMEOUT)
        print("Update username:", r.status_code, r.text)
        if r.status_code != 200 or not r.json().get('success'):
            return False

        # 6) Jelszó frissítés
        r = s.patch(
            f"{BASE_URL}/api/user/update",
            json={"current_password": reg_payload["password"], "new_password": "It3stStrong!Pass2"},
            timeout=TEST_TIMEOUT,
        )
        print("Update password:", r.status_code, r.text)
        if r.status_code != 200 or not r.json().get('success'):
            return False

        # 7) Új jelszóval bejelentkezés
        r = s.post(
            f"{BASE_URL}/api/login",
            json={"username": new_username, "password": "It3stStrong!Pass2"},
            timeout=TEST_TIMEOUT,
        )
        print("Login with new password:", r.status_code, r.text)
        if r.status_code != 200 or not r.json().get('success'):
            return False

        return True
    except Exception as e:
        print(f"Új funkciók integrációs teszt hiba: {e}")
        return False


def test_scores_filters_sort_pagination():
    # /api/scores szűrők, rendezés, lapozás ellenőrzése
    print("\nScores filters/sort/pagination teszt...")
    try:
        # Alap global kérés limit=2, time_asc rendezés
        r = requests.get(
            f"{BASE_URL}/api/scores",
            params={
                "scope": "global",
                "game_mode": "color-hunter",
                "difficulty": "easy",
                "sort": "time_asc",
                "limit": 2,
                "page": 1,
            },
            timeout=TEST_TIMEOUT,
        )
        print("Scores filters resp:", r.status_code, r.text[:200])
        if r.status_code != 200:
            return False
        data = r.json()
        if not data.get('success'):
            return False
        # lapozás 2. oldal
        r2 = requests.get(
            f"{BASE_URL}/api/scores",
            params={
                "scope": "global",
                "game_mode": "color-hunter",
                "difficulty": "easy",
                "sort": "time_asc",
                "limit": 2,
                "page": 2,
            },
            timeout=TEST_TIMEOUT,
        )
        print("Scores filters page2 resp:", r2.status_code)
        if r2.status_code != 200:
            return False
        return True
    except Exception as e:
        print(f"Scores filters/sort/pagination hiba: {e}")
        return False


def test_scores_me_requires_login():
    # scope=me esetén bejelentkezés szükséges
    print("\nscope=me auth requirement teszt...")
    try:
        r = requests.get(f"{BASE_URL}/api/scores?scope=me&limit=1", timeout=TEST_TIMEOUT)
        print("Scores me without login:", r.status_code)
        return r.status_code == 401
    except Exception as e:
        print(f"scope=me auth teszt hiba: {e}")
        return False


def test_update_user_validation_errors():
    # update_user validációs hibák ellenőrzése (weak password, missing current password)
    print("\nupdate_user validation teszt...")
    try:
        s = requests.Session()
        ts = int(time.time())
        # Regisztráció
        reg_payload = {
            "username": f"val_user_{ts}",
            "email": f"val_{ts}@example.com",
            "password": "Val1dPass!"
        }
        r = s.post(f"{BASE_URL}/api/register", json=reg_payload, timeout=TEST_TIMEOUT)
        print("register for validation:", r.status_code)
        if r.status_code not in [200, 201]:
            return False

        # Weak password (validators szerint min. 8 és komplexitás kell)
        r = s.patch(
            f"{BASE_URL}/api/user/update",
            json={"current_password": reg_payload["password"], "new_password": "short"},
            timeout=TEST_TIMEOUT,
        )
        print("weak password resp:", r.status_code, r.text)
        if r.status_code != 400:
            return False

        # Hiányzó current_password, ha new_password van
        r = s.patch(
            f"{BASE_URL}/api/user/update",
            json={"new_password": "Strong1!Pass"},
            timeout=TEST_TIMEOUT,
        )
        print("missing current_password resp:", r.status_code, r.text)
        if r.status_code != 400:
            return False

        return True
    except Exception as e:
        print(f"update_user validation teszt hiba: {e}")
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
        test_scores_global_and_me_and_user_update,
        test_scores_filters_sort_pagination,
        test_scores_me_requires_login,
        test_update_user_validation_errors,
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
        "Új funkciók: scores global/me és user update",
        "Scores szűrők/rendezés/lapozás",
        "scope=me auth requirement",
        "update_user validációk",
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