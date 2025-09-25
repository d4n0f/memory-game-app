from flask import Flask, render_template, request, send_from_directory, jsonify
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import os

app=Flask(__name__)

#Adatbázis konfiguráció inicializálása
db_config = {
    'host':'localhost',
    'user':'root',
    'password':'admin',
    'database':'memory_game',
    'charset':'latin2',
    'collation':'latin2_hungarian_ci'
}

# Mysql szerverrel való kapcsolat felépítése
def get_db_connect():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except mysql.connector.Error as err:
        print("MySQL kapcsolati hiba: {}".format(err))
        return None

def init_db():

    try:
        # Kapcsolat kialakítása adatbázis nélkül
        temp_config = db_config.copy()
        temp_config.pop('database')
        connection = mysql.connector.connect(**temp_config)
        cursor = connection.cursor()

        # Adatbázis létrehozása ha nem létezik
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_config['database']} CHARACTER SET {db_config['charset']} COLLATE {db_config['collation']}")
        cursor.execute(f"USE {db_config['database']}")

        # players tábla létrehozása az adatbázis diagram szerint
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_played TIMESTAMP NULL) ENGINE = InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        # scores tábla létrehozása az adatbázis diagram szerint
        cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS scores (
            id INT AUTO_INCREMENT PRIMARY KEY,
            player_id INT NOT NULL,
            score INT NOT NULL CHECK (score >= 0),
            game_mod Enum('easy', 'medium', 'hard') DEFAULT 'easy',
            game_time INT DEFAULT 0 CHECK (game_time >= 0),
            rounds_played INT DEFAULT 1 CHECK (rounds_played >= 1),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP) ENGINE = InnoDB DEFAULT CHARSET={db_config['charset']} COLLATE={db_config['collation']}''')
        connection.commit()
        print("Adatbázis és a táblák sikeresen létrehozva!")

    except mysql.connector.Error as err:
        print("MySQL adatbázis inicializásakor hiba lépet fel: {}".format(err))

#API végpontok
@app.route("/<path:filename>")
def server_static(filename):
    return send_from_directory(os.path.join(app.root_path, 'static'), filename)
@app.route('/')
def index():
    return render_template('color-hunter.html')
@app.route('/game')
def game():
    return render_template('color-hunter.html')
@app.route('/scores')
def scores():
    return render_template('scores.html')

#Adatbázis egeszségügyi ellenőrzés
@app.route('/api/health',)
def api_health():
    try:
        conn=get_db_connect()
        if conn is None:
            return jsonify({'status':'error',
                            'message': 'Database connection failed'}),500

        cursor=conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()

        cursor.close()
        conn.close()
        return jsonify({'status':'ok','database':'connected','time':datetime.now().isoformat()})
    except Error as e:
        return jsonify({'status':'error','message':str(e)}), 500

if __name__ == '__main__':
    print("Adatbázis inicializálása")
    init_db()
    print("Flask inditása")
    app.run(debug=True, host='0.0.0.0', port=5000)