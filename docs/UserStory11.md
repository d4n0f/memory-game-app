## Funkció: Többjátékos lobby a Színvadász módban

### 1

Szituáció: A felhasználó új lobbyt hoz létre

* Amennyiben a felhasználó a Színvadász mód kezdőfelületén tartózkodik
* Amikor rákattint az „Új lobby létrehozása” lehetőségre
* Akkor a rendszer létrehoz egy üres lobbyt, amelyhez más játékosok csatlakozhatnak

### 2

Szituáció: A játékos csatlakozik egy meglévő lobbyhoz

* Amennyiben a felhasználó a Színvadász lobbylista oldalán tartózkodik
* Amikor kiválaszt egy elérhető lobbyt és rákattint a „Csatlakozás” gombra
* Akkor a felhasználó belép a lobbyba, ahol látja a többi résztvevőt

### 3

Szituáció: A lobby megtelik

* Amennyiben a lobbyhoz játékosok csatlakoznak
* Amikor a lobbyban összesen négy játékos tartózkodik
* Akkor a lobby eléri a maximális létszámot, és több játékos nem csatlakozhat

### 4

Szituáció: A Színvadász játék elindul a lobbyban

* Amennyiben legalább két játékos tartózkodik a lobbyban
* Amikor a lobby tulajdonosa elindítja a játékot
* Akkor a rendszer minden játékos számára egyszerre elindítja a Színvadászt

### 5

Szituáció: A játékosok megkapják a színek megtekintésére szánt időt

* Amennyiben a játék elindult
* Amikor a rendszer megjeleníti a felvillanó színeket
* Akkor minden játékos a választott nehézségi szintnek megfelelő időt kap az áttekintésre

### 6

Szituáció: A játékosok megadják a válaszaikat

* Amennyiben a színek megtekintésének ideje lejárt
* Amikor minden játékos kiválasztja a szerinte helyes színt
* Akkor a rendszer rögzíti és időbélyeggel ellátva elmenti a válaszaikat

### 7

Szituáció: A leggyorsabb helyes válasz több pontot ér

* Amennyiben a játékosok válaszai elérhetőek
* Amikor a rendszer kiértékeli, ki válaszolt helyesen
* Akkor a leggyorsabban helyes választ adó játékos kapja a legtöbb pontot

### 8

Szituáció: A lassabb helyes válaszok kevesebb pontot érnek

* Amennyiben több játékos is helyes választ adott
* Amikor a rendszer időrendbe állítja a helyes válaszokat
* Akkor a második, harmadik és negyedik helyezett csökkenő mennyiségű pontot kap

### 9

Szituáció: Az eredménytábla megjelenik a forduló végén

* Amennyiben a rendszer kiszámolta a pontokat
* Amikor a fordulónak vége
* Akkor a játék egy eredménylistát jelenít meg a lobby minden játékosa számára a helyezésekkel és pontszámokkal
