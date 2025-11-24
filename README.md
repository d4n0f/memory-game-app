Memory Game App
======================================

Rövid leírás
-----------
Ez a projekt egy böngészőben futó memóriakártya- és színkereső játék gyűjtemény, amely egyszerű back-enddel (Flask + MySQL) és statikus front-enddel készült. A felhasználók regisztrálhatnak, bejelentkezhetnek, szerkeszthetik a profiljukat (felhasználónév, jelszó, profilkép), játszhatnak több játékmódban, és az eredményeik mentődnek az adatbázisba.

Főbb funkciók
------------
- Felhasználói regisztráció és bejelentkezés.
- Profil szerkesztése: felhasználónév, jelszó, kiválasztott profilkép.
- Két játék: "Card Match" (memóriakártya) és "Color Hunter" (kép alapján választás).
- Több játékmód / nehézség (pl. easy/medium/hard) és Fraktál mód a kártyajátéknál (klienstenger generált párok).
- Multiplayer mód: Color Hunter multiplayer (valós idejű többjátékos játék SocketIO-val).
- Pontszámok mentése és lekérése scoreboard nézethez.
- Kliens-oldali avatar választó (előre feltöltött avatarok).

Technológiák
------------
- Backend: Python 3.8+ + Flask + Flask-SocketIO
- Adatbázis: MySQL (mysql-connector-python használatával)
- Frontend: HTML, CSS, JavaScript (statikus fájlok a `src/frontend` alatt)
- Tesztelés: unittest (backend), Cypress (frontend E2E tesztek)
- Logging: Python logging modul (rotating file handlers)

Projekt struktúra (rövid)
-------------------------
- `src/backend/python/` – Flask alkalmazás és API végpontok.
  - `run.py` – fő belépési pont (Flask app indítása SocketIO-val)
  - `memory-game-app.py` – alternatív belépési pont
  - `app/` – fő alkalmazás modul
    - `config.py` – konfigurációs beállítások
    - `main.py` – Flask app inicializálás
    - `routes/` – route-okat tartalmazó modulok (`auth.py`, `game.py`, `scores.py`, `multiplayer.py`, `static.py`)
    - `models/` – adatbázis kapcsolódó segédfüggvények, user/players modellek (`database.py`, `user.py`)
    - `utils/` – segédfüggvények (`validators.py`, `helpers.py`, `logger.py`)
  - `tests/` – teszt fájlok
    - `unit_test.py` – unit tesztek (validátorok, helper függvények, modellek)
    - `integration_test.py` – integrációs tesztek (API végpontok)

- `src/frontend/` – statikus fájlok
  - `main/menu/` – bejelentkezés, regisztráció, profil, menü
  - `game/` – `card-match/`, `color-hunter/` játékok
  - `assets/images/avatars/` – előre feltöltött avatar képek (pl. `avatar1.jpg` … `avatar9.jpg`)
  - `tests/cypress/e2e/` – Cypress E2E tesztek

Követelmények
-------------
- Python 3.8+ telepítve
- MySQL szerver elérhető (helyi vagy távoli)
- Node.js (Cypress tesztekhez)
- Ajánlott: virtuális környezet használata (venv vagy conda)

Telepítés és futtatás (fejlesztői mód)
-------------------------------------
1. Klónozd a repót és lépj be a mappába:

  ```powershell
  git clone <repository-url>
  cd memory-game-app
  ```

2. Hozz létre és aktiválj egy virtuális környezetet (PowerShell):

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Telepítsd a szükséges Python csomagokat:

   ```powershell
   pip install Flask flask-socketio mysql-connector-python python-dotenv werkzeug
   ```

   Vagy használj `requirements.txt` fájlt, ha létezik:
   ```powershell
   pip install -r requirements.txt
   ```

4. Telepítsd a frontend függőségeket (Cypress tesztekhez):

   ```powershell
   npm install
   ```

5. Környezeti változók (`.env`) — fontos: a `.env` fájlt NE add hozzá a verziókezeléshez (ne commit-eld).

  Hozz létre a `src/backend/python/.env` vagy a projekt gyökérben egy `.env` fájlt a saját környezetedhez illeszkedő értékekkel. Az alábbi minta csak placeholder-eket tartalmaz — cseréld ki a <...> értékeket a saját konfigurációdra:

  ```ini
  MYSQL_HOST=localhost
  MYSQL_USER=root
  MYSQL_PASSWORD=<your_password>
  MYSQL_DATABASE=memory_game
  MYSQL_CHARSET=utf8mb4
  MYSQL_COLLATION=utf8mb4_hungarian_ci

  FLASK_HOST=0.0.0.0
  FLASK_PORT=5000
  FLASK_DEBUG=True
  FLASK_SECRET_KEY=<your_secret_key>

  LOG_LEVEL=INFO
  ```


6. Inicializáld az adatbázist (a Flask indításakor az `init_db()` függvény megpróbálja létrehozni az adatbázist és a táblákat, ha szükséges). Indítsd el az alkalmazást:

   ```powershell
   python src\backend\python\run.py
   ```

   Vagy alternatív belépési pont:
   ```powershell
   python src\backend\python\memory-game-app.py
   ```

7. Nyisd meg a böngészőt: http://localhost:5000 (vagy a `FLASK_HOST:FLASK_PORT` értékének megfelelően)

API és route-ok (gyors áttekintés)
---------------------------------
- Oldalak (templates):
  - `/` – főoldal (menu / index)
  - `/menu` – játékmód választó
  - `/card-match` – memóriakártya játék
  - `/color-hunter` – kép választó játék
  - `/scores` – scoreboard
  - `/profile` – profil szerkesztése (template)
  - `/profile/avatar` – külön avatar választó oldal

- Static image route-ok (static.py definiálja):
  - `/assets/images/<filename>` – általános képek (itt található az `avatars/` mappa)
  - `/assets/images/color-match/<filename>` – color-match galéria
  - `/assets/images/color-hunter/<filename>` – color-hunter galéria

- API végpontok:
  - `POST /api/register` – regisztráció
  - `POST /api/login` – bejelentkezés
  - `POST /api/logout` – kijelentkezés
  - `GET /api/current-user` – aktuális felhasználó adatai
  - `PATCH /api/user/update` – felhasználó adatainak frissítése (username, password, profile_picture)
  - `GET /api/scores` – pontszámok lekérése
  - `POST /api/save` – pontszám mentése

- SocketIO események (multiplayer):
  - `connect` – kapcsolódás
  - `create_room` – szoba létrehozása
  - `join_room` – szobához csatlakozás
  - `leave_room` – szoba elhagyása
  - `start_game` – játék indítása
  - `submit_answer` – válasz beküldése
  - stb.

Frontend fejlesztési megjegyzések
---------------------------------
- Statikus fájlok a `src/frontend` mappában vannak. A Flask app statikus és templateroot-ját úgy állítottuk be, hogy innen szolgálja ki a fájlokat.
- Avatarok helye: `src/frontend/assets/images/avatars/avatar1.jpg` … `avatar9.jpg`. A Flask route `/assets/images/avatars/<file>` fogja kiszolgálni ezeket.
- A profiloldal és avatar választó kliens-oldali JS-sel kezel adatokat a fenti API-k felé.
- Multiplayer funkció SocketIO-val működik, valós idejű kommunikációhoz.

Adatbázis
---------
- A script `init_db()` létrehozza a szükséges táblákat, ha még nem léteznek.
- Felhasználó táblában van `profile_picture` oszlop — itt a kiválasztott avatar útvonala (pl. `/assets/images/avatars/avatar1.jpg`) tárolható.
- Táblák: `users`, `players`, `scores`, `game_sessions`

Tesztelés
---------
- **Unit tesztek**: A `src/backend/python/tests/unit_test.py` fájl tartalmazza az unit teszteket (validátorok, helper függvények, modellek tesztelése).

  Futtatás:
  ```powershell
  cd src/backend/python
  python -m pytest tests/unit_test.py
  ```
  
  Vagy PyCharm trial runner-rel:
  ```powershell
  trial tests.unit_test
  ```

- **Integrációs tesztek**: A `src/backend/python/tests/integration_test.py` fájl tartalmazza az integrációs teszteket (API végpontok tesztelése).

  Futtatás:
  ```powershell
  cd src/backend/python
  python -m pytest tests/integration_test.py
  ```

- **Frontend E2E tesztek**: Cypress tesztek a `src/frontend/tests/cypress/e2e/` mappában.

  Futtatás:
  ```powershell
  npm run cypress:open  # Interaktív mód
  npm run cypress:run   # Headless mód
  ```

Hasznos tippek és hibakeresés
----------------------------
- Ha a képek nem jelennek meg, ellenőrizd, hogy a fájlok léteznek a `src/frontend/assets/images/avatars/` mappában, és hogy a Flask app fut és a `/assets/images/...` útvonal működik.
- Ha adatbázis kapcsolati hibát kapsz, ellenőrizd a `.env` beállításokat és a MySQL hozzáférést.
- Böngésző cache: ha korábban rossz elérési utakat mentett a kliens, nyomj `Ctrl+F5`-öt a frissítéshez.
- SocketIO kapcsolati problémák esetén ellenőrizd, hogy a Flask-SocketIO telepítve van-e és a `run.py` helyesen inicializálja.
- Log fájlok: a `src/logs/` mappában találhatóak az alkalmazás log fájlok (`app.log`, `error.log`).
