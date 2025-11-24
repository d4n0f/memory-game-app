## Funkció: Színvadász játékmód (Singleplayer + Párbaj mód)

### 1
Szituáció: A felhasználó beállítja a nehézségi szintet

* Amennyiben a felhasználó bejelentkezik és a menü kezdőfelületén tartózkodik

* Amikor betöltődnek a nehézségi beállítások

* Akkor a rendszer megjeleníti a Könnyű, Közepes és Nehéz nehézségi opciókat

### 2
Szituáció: A felhasználó kiválaszt egy nehézségi szintet

* Amennyiben a nehézségi opciók láthatók

* Amikor a felhasználó rákattint a Könnyű, Közepes vagy Nehéz nehézségre

* Akkor a rendszer eltárolja a kiválasztott nehézségi szintet, amely a következő játékban érvényes lesz

## Singleplayer (Gyakorló mód)
### 3
Szituáció: A felhasználó a Singleplayer módot választja

* Amennyiben a felhasználó már beállította a nehézségi szintet és kiválasztotta a játékmódot

* Amikor rákattint az indítás gombra

* Akkor a rendszer a singleplayer/multiplayer kezdőfelületére irányítja

### 4
Szituáció: A felhasználó elindítja a gyakorlást

* Amennyiben a felhasználó a Singleplayer kezdőfelületén tartózkodik

* Amikor rákattint a játék indítás gombra

* Akkor a rendszer elindítja a Színvadász fordulót a korábban kiválasztott nehézségi beállítások szerint (megtekintési idő: Könnyű=10 mp, Közepes=5 mp, Nehéz=3 mp)

### 5
Szituáció: A játékos korlátlanul gyakorolhat

* Amennyiben egy forduló véget ért

* Amikor a felhasználó újabb fordulót szeretne játszani

* Akkor a rendszer új fordulót indít, ugyanazzal a nehézségi szinttel

## Párbaj mód (Multiplayer – több játékos)
### 6
Szituáció: A felhasználó Párbaj módot választ

* Amennyiben a Párbaj módot választja

* Amikor rákattint a „Párbaj mód” gombra

* Akkor a rendszer a Párbaj lobby felületére irányítja, amely többjátékos csatlakozásra alkalmas

### 7
Szituáció: A Párbaj lobby előkészül a játékra

* Amennyiben játékosok csatlakoznak a lobbyhoz

* Amikor legalább két játékos van jelen

* Akkor a rendszer lehetővé teszi a párbaj elindítását

### 8
Szituáció: A Párbaj menet elindul minden játékos számára

* Amennyiben 2 vagy több játékos készen áll

* Amikor a host elindítja a párbajt

* Akkor a Színvadász játék minden játékos számára egyszerre indul el

* Akkor a megtekintési idő minden játékosnál fixen 5 másodperc

### 9
Szituáció: A játékosok megadják a válaszaikat

* Amennyiben a megtekintési idő lejárt

* Amikor a játékosok kiválasztják a szerintük helyes színt

* Akkor a rendszer rögzíti a válaszaikat és elmenti

### 10
Szituáció: A rendszer megállapítja a helyezéseket

* Amennyiben a játékosok válaszai rögzítve lettek

* Amikor a rendszer ellenőrzi őket

* Akkor a leggyorsabban helyes választ adó játékos kapja a legtöbb pontot és a sorra következők a beküldési idejükhöz igazítottan csökkentett pontszámot kapnak.

### 11
Szituáció: A párbaj eredménye megjelenik

* Amennyiben a pontok kiszámításra kerültek

* Amikor a menet véget ér

* Akkor a rendszer megjeleníti a rangsort, minden játékos helyezésével és pontjaikkal
