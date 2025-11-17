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
- Pontszámok mentése és lekérése scoreboard nézethez.
- Kliens-oldali avatar választó (előre feltöltött avatarok).

Technológiák
------------
- Backend: Python 3.8+ + Flask
- Adatbázis: MySQL (mysql-connector-python használatával)
- Frontend: HTML, CSS, JavaScript (statikus fájlok a `src/frontend` alatt)

Projekt struktúra (rövid)
-------------------------
- `src/backend/python/` – Flask alkalmazás és API végpontok.
  - `memory-game-app.py` – belépési pont (Flask app konfiguráció, statikus fájlok és sablonok elérési útjai, init_db). 
  - `app/routes/` – route-okat tartalmazó modulok (`auth.py`, `game.py`, stb.).
  - `app/models/` – adatbázis kapcsolódó segédfüggvények, user/players modellek.
  - `memory-game-app-unit-test.py`, `memory-game-app-integration-test.py` – tesztek.

- `src/frontend/` – statikus fájlok
  - `main/menu/` – bejelentkezés, regisztráció, profil, menü
  - `game/` – `card-match/`, `color-hunter/` játékok
  - `assets/images/avatars/` – előre feltöltött avatar képek (pl. `avatar1.jpg` … `avatar9.jpg`)

Követelmények
-------------
- Python 3.8+ telepítve
- MySQL szerver elérhető (helyi vagy távoli)
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

3. Telepítsd a szükséges Python csomagokat. (A következő csomagok szükségesek: `Flask`, `mysql-connector-python`, `python-dotenv`, `werkzeug`.)

   Példa telepítés:
   ```powershell
   pip install Flask mysql-connector-python python-dotenv werkzeug
   ```

4. Környezeti változók (`.env`) — fontos: a `.env` fájlt NE add hozzá a verziókezeléshez (ne commit-eld).

  Hozz létre a `src/backend/python/.env` vagy a projekt gyökérben egy `.env` fájlt a saját környezetedhez illeszkedő értékekkel. Az alábbi minta csak placeholder-eket tartalmaz — cseréld ki a <...> értékeket a saját konfigurációdra:

  ```ini
  MYSQL_HOST=<MYSQL_HOST>
  MYSQL_USER=<MYSQL_USER>
  MYSQL_PASSWORD=<MYSQL_PASSWORD>
  MYSQL_DATABASE=<MYSQL_DATABASE>
  MYSQL_CHARSET=utf8mb4
  MYSQL_COLLATION=utf8mb4_hungarian_ci

  FLASK_HOST=127.0.0.1
  FLASK_PORT=5000
  FLASK_DEBUG=True
  SECRET_KEY=<SECRET_KEY>
  ```

  Tipp: soha ne helyezz el valódi jelszavakat vagy titkos kulcsokat nyilvános fájlokban.

5. Inicializáld az adatbázist (a Flask indításakor az `init_db()` függvény megpróbálja létrehozni az adatbázist és a táblákat, ha szükséges). Egyszerűen indítsd el az alkalmazást:

   ```powershell
   python src\backend\python\memory-game-app.py
   ```

   Megjegyzés: a fájl fejlettségének megfelelően létezik alternatív `run.py` belépési pont is; nyisd meg a `src/backend/python` mappát és kövesd az ottani útmutatót.

6. Nyisd meg a böngészőt: http://localhost:5000 (vagy a `FLASK_HOST:FLASK_PORT` értékének megfelelően)

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

- Static image route-ok (memory-game-app.py definiálja):
  - `/assets/images/<filename>` – általános képek (itt található az `avatars/` mappa)
  - `/assets/images/color-match/<filename>` – color-match galéria

- API végpontok (példák, auth.py):
  - `POST /api/register` – regisztráció
  - `POST /api/login` – bejelentkezés
  - `POST /api/logout` – kijelentkezés
  - `GET /api/current-user` – aktuális felhasználó adatai
  - `PATCH /api/user/update` – felhasználó adatainak frissítése (username, password, profile_picture)
  - `GET /api/scores` – pontszámok lekérése
  - `POST /api/save` – pontszám mentése

Frontend fejlesztési megjegyzések
---------------------------------
- Statikus fájlok a `src/frontend` mappában vannak. A Flask app statikus és templateroot-ját úgy állítottuk be, hogy innen szolgálja ki a fájlokat.
- Avatarok helye: `src/frontend/assets/images/avatars/avatar1.jpg` … `avatar9.jpg`. A Flask route `/assets/images/avatars/<file>` fogja kiszolgálni ezeket.
- A profiloldal és avatar választó kliens-oldali JS-sel kezel adatokat a fenti API-k felé.

Adatbázis
---------
- A script `init_db()` létrehozza a szükséges táblákat, ha még nem léteznek.
- Felhasználó táblában van `profile_picture` oszlop — itt a kiválasztott avatar útvonala (pl. `/assets/images/avatars/avatar1.jpg`) tárolható.

Tesztelés
---------
- Vannak egyszerű tesztesetek a `src/backend/python` mappában (`memory-game-app-unit-test.py`, `memory-game-app-integration-test.py`). Futattásuk előfeltétele a környezet és a telepített csomagok.

   Példa futtatás (virtuális környezetben):
   ```powershell
   python src\backend\python\memory-game-app-unit-test.py
   python src\backend\python\memory-game-app-integration-test.py
   ```

Hasznos tippek és hibakeresés
----------------------------
- Ha a képek nem jelennek meg, ellenőrizd, hogy a fájlok léteznek a `src/frontend/assets/images/avatars/` mappában, és hogy a Flask app fut és a `/assets/images/...` útvonal működik.
- Ha adatbázis kapcsolati hibát kapsz, ellenőrizd a `.env` beállításokat és a MySQL hozzáférést.
- Böngésző cache: ha korábban rossz elérési utakat mentett a kliens, nyomj `Ctrl+F5`-öt a frissítéshez.
