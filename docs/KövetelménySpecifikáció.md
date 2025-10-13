# Követelményspecifikáció - Memóriajáték Webalkalmazás

| Modul   | ID  | Név                          | Verzió | Kifejtés                                                                 |
| ------- | --- | ---------------------------- | ------ | ------------------------------------------------------------------------ |
| Backend | K1  | Flask alapú szerver          | 1.0    | Python Flask keretrendszer használata a backend kiszolgálásához          |
| Backend | K2  | REST API végpontok           | 1.0    | 3 REST végpont implementálása (pl. /api/scores, /api/newgame, /api/save) |
| Backend | K3  | Adatvalidáció                | 1.0    | Bejövő adatok validálása a szerver oldalon                               |
| Backend | K4  | Egyszerű routing             | 1.0    | 2 különböző útvonal kezelése (pl. /, /game, /scores)                     |
| Backend | K5  | Statikus fájlok kiszolgálása | 1.0    | CSS, JS és képfájlok kiszolgálása a Flask segítségével                   |
| HTML    | K6  | HTML5 szerkezet              | 1.0    | Modern HTML5 szerkezet használata semantic elemekkel                     |
| HTML    | K7  | Reszponzív design            | 1.0    | Oldal reszponzív legyen különböző képernyőméretekre                      |
| HTML    | K8  | Accessibility                | 1.0    | Alapvető accessibility követelmények betartása (ARIA attribútumok)       |
| HTML    | K9  | Meta tag-ek                  | 1.0    | Megfelelő meta tag-ek használata (viewport, charset, description)        |
| HTML    | K10 | Form elemek                  | 1.0    | Legalább 1 form elem használata (pl. név megadása játék elején)          |
| CSS        | K11 | Grid vagy Flexbox         | 1.0    | Modern elrendezési technológiák használata a kártyák elrendezéséhez      |
| CSS        | K12 | Animációk                 | 1.0    | CSS animációk implementálása a kártyafordításhoz                         |
| CSS        | K13 | Reszponzív design (CSS)   | 1.0    | Media query-k használata különböző képernyőméretekhez                    |
| CSS        | K14 | Átlátható kódstruktúra    | 1.0    | Jól szervezett CSS, következetes naming convention                       |
| CSS        | K15 | Kártya design             | 1.0    | Esztétikus kártya design előoldallal és hátoldallal                      |
| JavaScript | K16 | DOM manipuláció           | 1.0    | JavaScript alapú DOM manipuláció a kártyák kezeléséhez                   |
| JavaScript | K17 | Eseménykezelés            | 1.0    | Egérkattintás és eseménykezelés a kártyákhoz                             |
| JavaScript | K18 | Időzítők                  | 1.0    | setTimeout/setInterval használata a játéklogikához                       |
| JavaScript | K19 | Fetch API                 | 1.0    | Fetch használata a backend kommunikációhoz                               |
| JavaScript | K20 | Játékállapot kezelés      | 1.0    | Játékállapot nyomon követése JavaScript                                  |
| CSS       | K21 | Egységes design         | 1.0    | Következetes színskála és design a teljes alkalmazásban                 |
| CSS       | K22 | Kártya design           | 1.0    | Esztétikus és felhasználóbarát kártya design                            |
| CSS       | K23 | Typography              | 1.0    | Olvasható és megfelelő méretű betűtípusok használata                    |
| CSS       | K24 | Reszponzív design       | 1.0    | Design, amely minden eszközön jól működik                               |
| CSS       | K25 | Interakció visszajelzés | 1.0    | Vizualizáció a felhasználói interakciókról (hover, click stb.)          |
| Backend   | K26 | Dokumentáció            | 1.0    | A kód megfelelő kommentelése és dokumentálása                           |
| Backend   | K27 | Verziókövetés           | 1.0    | Git használata a verziókövetéshez                                       |
| Backend   | K28 | Hibakezelés             | 1.0    | Alapvető hibakezelés implementálása                                     |
| Backend   | K29 | Böngésző kompatibilitás | 1.0    | Támogatás a legfrissebb böngészőkben                                    |
| Backend   | K30 | Teljesítmény            | 1.0    | Optimális teljesítmény és gyors betöltési idők                          |
| Adatbázis | K31 | Táblatervezés           | 1.0    | Legalább 2 tábla létrehozása (pl. players, scores)                      |
| Adatbázis | K32 | Adatintegritás          | 1.0    | Megfelelő mezőtípusok és kulcsok használata                             |
| Adatbázis | K33 | CRUD műveletek          | 1.0    | Create, Read, Update, Delete műveletek implementálása                   |
| Adatbázis | K34 | Kapcsolatok             | 1.0    | Táblák közötti kapcsolatok kialakítása                                  |
| Adatbázis | K35 | Adatbiztonság           | 1.0    | Alapvető adatbiztonsági intézkedések (SQL injection védelem)            |
| Auth | K36 | Felhasználó regisztráció	  | 1.1    | Regisztrációs rendszer email és felhasználónév ellenőrzéssel            |
| Auth | K37 | Bejelentkezési rendszer		  | 1.1    | Biztonságos bejelentkezés session kezeléssel           |
| Auth | K38 | Jelszó titkosítás		  | 1.1    | Werkzeug Security használata jelszavak hash-elésére           |
| Auth | K39 | Session kezelés		  | 1.1    | Flask session management a felhasználói állapot követésére     |
| Auth | K40 | Kijelentkezés		  | 1.1    | Session törlés és biztonságos kijelentkezés     |
| Game | K41 | Több játékmód		  | 1.1    | Color Hunter és Card Match játékmódok implementálása    |
| Game | K42 | Nehézségi szintek		  | 1.1    | Easy, Medium, Hard nehézségi szintek különböző paraméterekkel   |
| Game | K43 | Game Session kezelés			  | 1.1    | Játék session-ök nyomon követése start/end időpontokkal  |
| Game | K44 | Valós idejű játékállapot		  | 1.1    | Játékállapot frissítése minden körben  |
| Game | K45 | Időmérés	  | 1.1    | 	Játékidő mérése és rögzítése  |
| Scores | K46 | Részletes statisztikák	  | 1.1    | 	Játékidő, körök száma, pontszám részletes rögzítése  |
| Scores | K47 | Szűrhető ranglista		  | 1.1    | 	Eredmények szűrése játékmód és nehézség szerint |
| Scores | K48 | Játékos profilok	  | 1.1    | 	Játékos statisztikák (legtöbb játék, legjobb pontszám) |
| Scores | K49 | Valós idejű eredményfrissítés	  | 1.1    | 	Eredmények azonnali megjelenítése mentés után |
| Scores | K50 | Toplisták  | 1.1    | 	Legjobb játékosok listázása különböző kategóriákban |
| Testing | K51 | Unit tesztek  | 1.1    | 	Backend funkciók unit tesztelése Python unittest modullal |
| Testing | K52 | Integrációs tesztek | 1.1    | 	API végpontok integrációs tesztelése |
| Testing | K53 | Mock adatbázis kapcsolat	| 1.1    | 	Tesztkörnyezet mock objektumokkal |
| Testing | K54 | Teszt konfiguráció		| 1.1    | 	Külön teszt konfiguráció és adatbázis |
| Testing | K55 | Automatikus tesztfuttatás			| 1.1    | 	Tesztcsomagok automatikus futtatása és jelentés generálás |
| Backend | K56 | RESTful API design			| 1.1    | 	Megfelelő HTTP státuszkódok és REST konvenciók használata |
| Backend | K57 | Komplex adatvalidáció			| 1.1    | 	Email, jelszó erősség, felhasználónév validáció |
| Backend | K58 | Környezeti konfiguráció		| 1.1    | 	.env fájl alapú konfiguráció kezelés |
| Backend | K59 | Adatbázis migráció		| 1.1    | 	Automatikus adatbázis inicializálás és séma frissítés |
| Backend | K60 | Hibakezelés és logging		| 1.1    | 	Részletes hibanaplózás és felhasználóbarát hibaüzenetek |
| Tech | K61 | Moduláris kódstruktúra		| 1.1    | 	Szeparált router, model, utility modulok |
| Tech | K62 | Biztonsági intézkedések			| 1.1    | 	SQL injection védelem, XSS prevention |
| Tech | K63 | Teljesítmény optimalizálás			| 1.1    | 	Adatbázis kapcsolat pooling, query optimalizálás |
| Tech | K64 | Skálázhatóság			| 1.1    | 	Tervezési minták alkalmazása bővítéshez |
| Tech | K65 | Kódminőség			| 1.1    | Clean code, következetes naming convention, code documentation |