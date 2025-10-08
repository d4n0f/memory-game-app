import requests
import json

BASE_URL = "http://localhost:5000"


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
        data = {"name": "TesztJatekos"}
        response = requests.post(f"{BASE_URL}/api/game", json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Új játék hiba: {e}")
        return False


def test_save_score():
    #Eredmény mentés teszt
    print("\nEredmény mentés teszt...")
    try:
        data = {
            "player_id": 2,
            "score": 150,
            "game_mode": "color-hunter",
            "difficulty": "medium",
            "game_time": 120,
            "rounds_played": 5
        }
        response = requests.post(f"{BASE_URL}/api/save", json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Eredmény mentés hiba: {e}")
        return False


def test_get_scores():
    #Eredmények lekérés teszt
    print("\nEredmények lekérés teszt...")
    try:
        response = requests.get(f"{BASE_URL}/api/scores?game_mode=medium&limit=5")
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Talált eredmények: {result.get('count', 0)}")
        return response.status_code == 200
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
            for player in players:
                print(
                    f"  - {player['name']}: {player['games_played']} játék, legjobb: {player.get('best_score', 'N/A')}")

            return True
        else:
            print(f"Hiba a válaszban: {result.get('error', 'Ismeretlen hiba')}")
            return False

    except Exception as e:
        print(f"Játékosok lekérés hiba: {e}")
        return False

def run_all_tests():
    #Összes teszt futtatása"""
    print("Backend tesztek indítása...")

    tests = [
        test_health,
        test_new_game,
        test_save_score,
        test_get_scores,
        test_get_players
    ]

    passed = 0
    for test in tests:
        if test():
            passed += 1
            print("Sikeres")
        else:
            print("Sikertelen")

    print(f"\n Eredmény: {passed}/{len(tests)} teszt sikeres")

    if passed == len(tests):
        print("Minden teszt sikeres! A backend működik.")
    else:
        print("Néhány teszt sikertelen. Ellenőrizd a backend-et.")


if __name__ == "__main__":
    run_all_tests()