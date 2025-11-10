# Rendszerterv

1. ## A rendszer célja:

   A webalkalmazás célja hogy a felhasználó egy memóriajátékot játszon és fejlessze a memóriáját. Felhasználó képes 3 nehézségi szint közül választani 2 játékmód közül. Felhasználónak van lehetősége nevet választani és később az elért pontokat is láthatja a játék után. Fontos, hogy a felhasználó könnyen el tudjon igazodni a felületeken ezért minimalista felhasználói felületet kap a program.
   Minden elért eredményt adatbázisban tárol a program így visszatudja keresni az előző eredményeket. A rendszer kizárólag webes környezetben lesz használható. Top listán fog megjeleni a felhasználók eremédnye. A webalkalmazás belépési pontja egy belépési felületre mutat így belépés után fog tudni játszani a felhasználó a játékkal. Van arra is lehetősége a felhasználók hogy vendégként lépjen be viszont abban az esetben ideglenesen tárolódnak az adatok. A fő felhasználó bázis célunk igazából a teljes korosztály viszont szeretnénk szakembereknek is segítséget nyújtani a gyermekek fejlesztésében.

2. ## Projekterv

   **Projektszerepkörök, felelőségek:**

   - Scrum master: Tassi Bence
   - Product owner: Fónád Bálint

     - **Projektmunkások és felelőségek:**

     - Backend és Teszt: Tassi Bence, feladata az adatok tárolásához szükséges adatszerkezetek kialakítása,funkciók létrehozása, a különböző platformok kiszolgálása adatokkal, adatbázis és a frontend elemek összekapcsolása.Felelőse a bejelentkezési és regisztráció funkció megfelelő validálásáert illetve adatbázisban való biztonságos tárolásért. Authentikációs és validálási metódusok kidogozásáért felelős. 
     Teszt oldalon minden funkciójának ellenőrzése, hibák felderítése és dokumentálása. Teszteli a kártyafordítás működését, a párosítási logikát, az időzítő pontos működését, az adatbázis-mentést és a különböző böngészőkben való megfelelő működést. Jelenti a talált hibákat és segít a minőségbiztosításban.

     - Frontend: Fónad Bálint és Spišáková Antónia, weboldal vagy alkalmazás felhasználói felületének (UI) és felhasználói élményének (UX) kialakításáért és megvalósításáért felelős. Dizájnok kódolása, interaktív elemek létrehozása, valamint annak biztosítása, hogy a felület gyors, stabil és intuitív legyen. Animációk minél folyékonyabb megjelenéséért és minél esztétikusabb kidolgozásáért. A frontendadatok megfelelő formátumú adat küldésért a backend felé.

     - Design: Spišáková Antónia, esztétikus és felhasználóbarát megjelenésének kialakítása. Ez magában foglalja a színpaletta, tipográfia és vizuális stílus meghatározását, a kártyák és felületi elemek designját, valamint az animációk és átmenetek tervezését. A designer felelős azért, hogy a játék reszponzív legyen minden eszközön, és hogy intuitív felhasználói élményt nyújtson a játékosoknak.

   **Űtemterv:**
   | Funkció | Feladat | Prioritás | Becslés | Aktuális idő | Eltelt idő| Hátralévő idő |
   |-----------|-----------|---|----|----|------|-------|
   Követelmény specifikáció| | 1 | 4 | 4| 4| 0|
   Rendszerterv| | 1 | 3 | 3 | 2 | 1|
   Funkcionális specifikáció| | 1 | 2 | 2 | 2 | 0|
   Use-case modell | | 1 | 1 | 1 | 1| 0|
   Adatbázis modell| | 2 | 2 | 2 | 2| 0|
   Adattárolás | Adatmodel megtervezése | 2 | 1 | 1 | 1 | 0|
   | |Adatbázis megvalósítása a szerveren | 2 | 3 | 3 | 0 | 3|
   Frontend | Frontend megtervezése | 2 | 4 | 4 | 3 | 1|
   || Frontend implementálás | 2 | 20 | 20 | 15 | 5|
   || Script fájlok elkészítése | 2 | 10 | 10 | 7 | 3|
   || HTML fájlok elkészítése | 2 | 2 | 2 | 1.5 | 0.5 |
   || CSS fájlok elkészítése | 2 | 3 | 3 | 3 | 3 |
   || Frontend teszt elkészítése | 2 | 5 | 5 | 0 | 5 |
   Design | Design megtervezése | 2 | 5 | 5 | 5 | 0|
   || Design implementálás | 2 | 3 | 3 | 3 | 0|
   || UI megtervezése | 2 | 2 | 2 | 2 | 0|
   Backend | Backend megtervezése | 2 | 10 | 10 | 10 | 0|
   || Backend implementálása | 2 | 50 | 50 | 30 | 20 |
   || Backend unit teszt | 2 | 5 | 5 | 3 | 2|
   || Backend integration teszt | 2 | 4 | 4 | 2 | 2|

   **Mérföldkövek:**

   - 🔄  Előírt modellek és dokumentumok elkészítése.
   - ✅  Adatmodell elkészítése megtörtént bemutatásra vár.
   - ✅  Frontend implementáció nagy részt elkészült átadásra vár.
   - ✅  Backend implementáció elkészült átadásra.
   - ✅  Program közel teljes designja és UI-ja elkészült bemutatásra vár.
   - ✅  Frontend POST metódusok elkészítése (api.js postJSON függvény).
   - ✅  A projekt demója elkészült bemutatásra vár.
   - ✅  Login backend elkészítése
   - ✅  Login frontend elkészítése
   - ✅  Teljes UI design kialaktása
   - ✅ Alap két játék mód átadva, müködik.
   - ⏳  Új játékmódok kidolgozása
   - ⏳  Kártyák elkészítése új játékmódokhoz
   - ⏳  Avatar választó felület és funkció teljes megvalósítása (backend támogatás kész, frontend hiányzik).
   - ⏳  Profil szerkesztés oldal frontend megvalósítása (backend API kész: /api/user/update).
   - ⏳  Eredmények/scores oldal frontend megvalósítása (backend API kész: /api/scores, route: /scores).
   - 🔄  Tesztek elkészítése (Cypress E2E tesztek elkészültek, unit/integration tesztek ellenőrzésre várnak).
   - 🔄  Játék teljes bemutatása (fő funkciók működnek, finomhangolás folyamatban).

3. ## Üzleti folyamatok modellje:

   ![Üzleti folyamatok modellje](BPM.png)

4. ## Követelmények:

- Funkcionális követelmények:
  - Felhasználó adatainak tárolása.
  - Webes környezteben müködik az alkalmazás.
  - Felhasználóknak adatai listázása.
  - Felhasználónak lehetőséget adni több nehezségi szint közül választani.
  - Adatvalidáció megoldása.
  - Reszponzívitás megoldása.
  - Átlátható kódstruktúrai megoldás.
  - Eseménykezelés megoldása.
  - Vizuális megoldás az interakciókról.
  - Bejelentkezési és regisztációs felület kialakítása.
  - Felhasználói adatok módosítására szolgáló felület kidolgozása.
  - Adatbázisba való bejelentkezési és regisztrációs adatok tárolása.
  - Avatar választó felület megoldása.
  - Avatar adatbázisba való tárolás megoldása.
  - Validációs és autentikációs metódusok megoldása backendben.

- Nem funkcionális követelmények:
  - A felhasználó képes fejleszteni a saját memóriáját és ezzel pontokat szerezhet.
  - Különböző szintek és játékmódok közül választhat a felhasználó igényei szerint.
  - Felhasználók top lista szerűen hasonlíthatják egymás eredményeit a sajátjaikhoz, verseny szellem kialakulása.
  - Játékos létrehozhat fiókot és saját igényei szerint módosíthaja az avatárját, jelszavát és felhasználónevét.

5. ## Funkcionális terv

   **Rendszerszereplők:**

   - Admin
   - Játékos

     - **Rendszerhasználati esetek és lefutásaik:**

     - Admin:

       - A felhasználói adatokat láthatja, változtathatja
       - Szerkesztheti vagy törölheti a felhasználói fiókokat
       - Módosíthatja a játékosok neveit, statisztikáit
       - Plusz nehézségi szintek létrehozzása
       - Játékeseteket átlátja
       - Láthatja az összes játék eredményét
       - Ellenőrizheti és kezelheti a ranglistát
       - Módosíthatja a pontszámítási algoritmust
       - Aktív felhasználók számának nyomon követése
       - Legnépszerűbb játékmódok elemzése
       - Átlagos játékidők és pontszámok megtekintése
       - Problémás játékterületek felderítése
       - Adatbázis karbantartás
       - Rendszer naplók megtekintése
       - Adatvédelem biztosítása
       - Teszt játékok indítása
       - Játékmechanikák tesztelése különböző konfigurációkban
       - Problémás helyzetek kezelése

     - Játékos:
       - Játékmódok választása
       - Program használata
       - Látja a toplistát de nem tudja módosítani
       - Ereményért pontokat kapnak egy pontozási rendszer szerint
       - Saját profil létrehozása
       - Személyes statisztikák mentése
       - Adatvédelmi garancia
       - Vendég játékos profil létrehozása
       - Vendég játékos esetén ideiglenes eredménymentés
       - Nehézségi szint beállítása
       - Legjobb pontszámod megtekintése
       - Utolsó játékod ideje
       - Jelszó védelme csak te férhetsz hozzá a fiókodhoz
       - Jogod van a törléshez - bármikor kérheted adataid törlését

   - **Menü-hierarchiák:**
    - BEJELENTKEZÉS
      - Bejelentkezés
      - REGISZTRÁCIÓ
        - Regisztráció
    - MAIN MENÜ
      - PROFIL SZERKESZTÉS
        - Profil szerkesztés
      - EREDMÉNY MEGTEKINTÉSE
        - Saját scoreboard
        - Globális scoreboard
      - Nehézség kiválasztása
      - Játékmód kiválasztása
    - SZÍNVADÁSZ 
      - Játék játszása
    - KÁRTYAPÁROSÍTÓ
      - Játék játszása
6. ## Fizikai környezet
   - Az alkalmazás csak webes platformra készül.
   - Backend valósítsa meg a frontend és adatbázis kapcsolatot.
   - Nincsenek megvásárolt komponenseink.
   - Fejlesztői eszközök:
     - Visual Studio Code
     - Pycharm
     - Flask Framework
     - Pytest
     - Mysql Workbench
7. ## Architekturális terv

   - Backend: A backend rendszer egy Python alapú RESTful API, amely a Flask keretrendszerre épül. Az API teljes körű felhasználókezelést, játékmenet-vezérlést és adatkezelést biztosít. A szerver MySQL adatbázissal kommunikál, amely a felhasználói adatokat, játékeredményeket és statisztikákat tárolja.

   - Web kliens: A webes kliensoldali alkalmazás HTML5, CSS3 és JavaScript technológiákkal készült, biztosítva a modern böngészőkompatibilitást és reszponzív viselkedést. A rendszer komplex biztonsági architektúrával rendelkezik, amely megvédi az adatokat és biztosítja a rendszer integritását.Login megadása után rest api, api-keyek segítségével ad hozzáférést a játékhoz és adatokhoz.

8. ## Adatbázis terv:

   ![Adatbázis_modell](Adatbázis_modell.png)

9. ## Implementációs terv:

   - Web: A Webes felület főként HTML5, CSS3, és Javascript nyelven fog készülni. Ezeket a technológiákat amennyire csak lehet külön fájlokba írva készítjük, és úgy fogjuk egymáshoz csatolni a jobb átláthatóság, könnyebb változtathatóság, és könnyebb bővítés érdekében. Képes lesz felhasználni a Backend részen futó REST szolgáltatás metódusait, ezáltal tud felvinni és lekérdezni adatokat az adatbázisból. Flask keretrendszert használunk a backend megvalósításához hogy könnyen meg tudjuk valósítani a kommunikációt a MySql szerver és Kliens között. A MySQL adatbázisban négy relációs táblát valósítunk meg, amelyek hierarchikusan kapcsolódnak egymáshoz. Az adatbázis magja a users tábla, amely az alapvető felhasználói fiókokat tárolja egyedi azonosítóval, felhasználónévvel, email címmel, titkosított jelszóval, profilkép elérési úttal, aktív státusszal, valamint a regisztráció és utolsó bejelentkezés időpontjaival. A players tábla a játékos profilokat kezeli, amely kapcsolódik a users táblához through a user_id külső kulcs segítségével. Itt található a játékos egyedi azonosítója, a megjelenítendő név, az összes játszott játék száma, a legjobb pontszám, valamint az utolsó játék időpontja és a profil létrehozásának időbélyege. A game_sessions tábla rögzíti a játék munkamenetek részleteit, beleértve a játékos azonosítóját, a játékmód típusát, a nehézségi szintet, valamint a munkamenet kezdetét és végét, valamint a teljes játékidőt. Végül a scores tábla tárolja a játékosok pontszámait és teljesítményét, kapcsolódva mind a game_sessions, mind a players táblákhoz. Itt található az elért pontszám, a játszott körök száma, és különösen fontos a game_time mező, amely a játék idejét tárolja másodpercben. Kiemelendő, hogy ezt az időt a kliens oldal számolja ki és küldi a szervernek, ezzel biztosítva, hogy ne legyenek eltérések az időmérésben a különböző rendszerek között. Az eredmény rögzítésének időpontját a created_at mező tárolja.

10. ## Tesztterv:
    A tesztelések célja a rendszer és komponensei funkcionalitásának teljes vizsgálata, ellenőrzése, a rendszer által megvalósított üzleti szolgáltatások verifikálása.

- **Unit tesztek:**
  A fejlesztési folyamat során folyamatosan kell tesztelni a metódusok funkcionalitását. Minden metódushoz Unit teszteket kell írni, amelyekkel elérjük a minél nagyobb kódlefedettséget. Egy metódus akkor tekinthető késznek, ha a hozzá tartozó tesztesetek hiba nélkül lefutnak.
- **Tesztelendő funkciók:**

  **Játék logikája:**
  Szükséges a játék mindkettő funkcióját tesztelni, ugyanis az egyik játékmód az idő alapú nem e fut túl az időn a játékos ha igen akkor át kell lépnie a scoreboardra.Játék módok esetén a pont a játék mód nehézsége is meghatározza. A leggyengébb játékmód az időalapú ott score adattagot nehézség határozza meg és a találat száma. A párosítás alapú játékmódnál a találatok száma és a játékmód nehézsége határozza meg. Ezeket szűkséges tesztelni.

  **Scoreboard**:
  Adatbázis oldalról megfelelően jelenti meg a neveket és a scoreokat. Ezt backend oldaról kapcsolatokat teszteljük.
  Fel kell tudnia tölteni, és le kell tudnia kérdezni az adatbázis adatait amit backend oldalról teszteljük. Frontend oldalról adatokat megfelelően kell tudnia a backend felé amit backend feldolgoz és adatbázis szerveren tárol így jön létre a kommunikáció. Kommunikációt szükséges tesztelnünk hogy megfelelően felépüljön. Adatintegritást, -validációt kell tesztelnünk.

  **Kártya fordtása:**
  Frontend oldalról szükséges tesztelni az animációkat ezt esztétikus implementációt követel meg. Magát a funkciót szükséges implementálás után tesztelni. Ez alapján score változó számolódik így fontos a funkció megfelelő müködése. A kártyának két oldala van így a visszafordulását is figyelni kell hogy jó e az adott kártya párja.