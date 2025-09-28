from flask import Flask, render_template, request, send_from_directory, jsonify
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import os


load_dotenv()  #.env fájl betöltése
app=Flask(__name__ )

BASE_DIR = os.path.dirname(os.path.abspath('..'))
FRONTEND_DIR = os.path.join(BASE_DIR, os.getenv('FRONTEND_PATH', 'frontend'))

app.static_folder = FRONTEND_DIR
app.template_folder = FRONTEND_DIR

#Adatbázis konfiguráció inicializálása
db_config = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user':os.getenv('MYSQL_USER', 'root'),
    'password':os.getenv('MYSQL_PASSWORD', 'admin'),
    'database':os.getenv('MYSQL_DATABASE', 'memory_game'),
    'charset': os.getenv('MYSQL_CHARSET','utf8mb4'),  # UTF-8 támogatás módosítva
    'collation': os.getenv('MYSQL_COLLATION','utf8mb4_hungarian_ci')
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
            game_mode Enum('easy', 'medium', 'hard') DEFAULT 'easy',
            game_time INT DEFAULT 0 CHECK (game_time >= 0),
            rounds_played INT DEFAULT 1 CHECK (rounds_played >= 1),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP) ENGINE = InnoDB DEFAULT CHARSET={db_config['charset']} COLLATE={db_config['collation']}''')
        connection.commit()
        print("Adatbázis és a táblák sikeresen létrehozva!")

    except mysql.connector.Error as err:
        print("MySQL adatbázis inicializásakor hiba lépet fel: {}".format(err))
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

#API végpontok
@app.route("/<path:filename>")
def server_static(filename):
    return send_from_directory(os.path.join(app.root_path, 'static'), filename)
@app.route('/')
def index():
    return render_template('main/menu/index.html')

@app.route('/menu')
def game_menu():
    return render_template('main/menu/gamemode-selector.html')

@app.route('/color-hunter')
def game():
    return render_template('game/color-hunter/color-hunter.html')

@app.route('/card-match')
def game2():
    return render_template('game/card-match/card-match.html')
@app.route('/scores')
def scores():
    return render_template('main/scoreboard/scores.html')

# ==================== STATIC FÁJLOK JAVÍTVA ====================

@app.route('/styles/<path:filename>')
def serve_css(filename):
    return send_from_directory(os.path.join(FRONTEND_DIR, 'styles'), filename)

@app.route('/scripts/<path:filename>')
def serve_js(filename):
    return send_from_directory(os.path.join(FRONTEND_DIR, 'scripts'), filename)

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory(os.path.join(FRONTEND_DIR, 'game','color-hunter','assets','images'), filename)


# ==================== SEGÉDFÜGGVÉNYEK ====================

def create_or_get_player(player_name):
    #Játékos létrehozása vagy lekérése
    try:
        conn = get_db_connect()
        if not conn:
            return None

        cursor = conn.cursor()

        # Játékos keresése
        cursor.execute("SELECT id FROM players WHERE name = %s", (player_name,))
        existing_player = cursor.fetchone()

        if existing_player:
            player_id = existing_player[0]
            # Frissítjük az utolsó játék időpontját
            cursor.execute("UPDATE players SET last_played = CURRENT_TIMESTAMP WHERE id = %s", (player_id,))
        else:
            # Új játékos létrehozása
            cursor.execute("INSERT INTO players (name, last_played) VALUES (%s, CURRENT_TIMESTAMP)", (player_name,))
            player_id = cursor.lastrowid

        conn.commit()
        cursor.close()
        conn.close()

        return player_id

    except Error as e:
        print(f"Játékos kezelési hiba: {e}")
        return None

# ==================== FORM KEZELÉS + ÁTIRÁNYÍTÁS ====================

@app.route('/start-game', methods=['POST'])
def start_game():
    #Játék indítása a főoldalról
    player_name = request.form.get('player_name', '').strip()

    if not player_name:
        return redirect(url_for('index', error='Nincs név megadva'))

    # Játékos mentése session-be
    session['player_name'] = player_name
    session['player_id'] = create_or_get_player(player_name)

    return redirect(url_for('game_menu'))


@app.route('/select-mode', methods=['POST'])
def select_mode():
    #Játékmód kiválasztása
    game_mode = request.form.get('game_mode', 'color-hunter')
    difficulty = request.form.get('difficulty', 'easy')

    session['game_mode'] = game_mode
    session['difficulty'] = difficulty

    if game_mode == 'color-hunter':
        return redirect(url_for('game'))
    else:
        return redirect(url_for('game2'))
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

@app.route('/api/game',methods=['POST'])
def new_game():
    #Új játék inditás
    try:
        data=request.get_json()

        if not data or 'name' not in data:
            return jsonify({'success':False,
                            'error':'missing name'}), 400
        conn= get_db_connect()
        if conn is None:
            return jsonify({'success':False,
                            'error':'database connection failed'}),500
        cursor=conn.cursor()
        # Játékos keresése ha létezik
        cursor.execute("SELECT id FROM players WHERE name=%s", (data['name'],))
        existing_player = cursor.fetchone()

        #Frissitjük a last_played mezőt
        if existing_player:
            player_id = existing_player[0]
            cursor.execute('UPDATE players SET last_played = CURRENT_TIMESTAMP WHERE id=%s', (player_id,))

            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'success': True,
                            'player_id': player_id,
                            'name': data['name'],
                            'message': 'Játék folytatódik'}), 200
        #Létrehozzuk a játékost ha nincs létrehozzva
        else:
            cursor.execute('INSERT INTO players(name, last_played) VALUES (%s, CURRENT_TIMESTAMP)',(data['name'],))
            player_id = cursor.lastrowid

            conn.commit()
            cursor.close()
            conn.close()

            return jsonify({'success':True,
                            'player_id':player_id,
                            'name':data['name'],
                            'message':'new game created'}), 201
    except Error as e:
        if conn and conn.is_connected():
            conn.rollback()
            cursor.close()
            conn.close()
        return jsonify({'success':False,
                        'error':f'Adatbázis hiba: {str(e)}'}),500
    except Exception as e:
        return jsonify({'success':False,
                        'error':f'Szerver hiba: {str(e)}'}),500

@app.route('/api/save',methods=['POST'])
def save_scores():
    #Eredmények mentése
    try:
        data = request.get_json()
        required_fields = ['player_id','score','game_mod','game_time','rounds_played']
        for field in required_fields:
            if field not in data:
                return jsonify({'success':False,
                                'error':f'missing {field}'}), 400
            player_id=int(data['player_id'])
            score=int(data['score'])
            game_mod=data['game_mod']
            game_time=int(data.get('game_time',0))
            rounds_played=int(data.get('rounds_played',1))

            #Validáció
            if score< 0 or game_time < 0 or rounds_played < 1:
                return jsonify({'success':False,
                                'error':f'Érvénytelen érték'}), 400
            if game_mod not in ['easy','medium','hard']:
                game_mod='easy'
            conn= get_db_connect()
            if conn is None:
                return jsonify({'success':False,
                                'error':'Adatbázis kapcsolat hiba'}),500
            cursor = conn.cursor()
            #Ellenőrizzük hogy létezik-e a játékos
            cursor.execute("SELECT id FROM players WHERE id=%s", (player_id,))
            if not cursor.fetchone():
                return jsonify({'success':False,
                                'error':'Játékos nem található'}),404
            #Eredmények mentése
            cursor.execute('''
                INSERT INTO scores (player_id, score, game_mod, game_time, rounds_played)
                VALUES (%s, %s, %s, %s, %s)
            ''', (player_id, score, game_mod, game_time, rounds_played))
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'success':True,
                            'message':'Eredmény sikeresen mentve',
                            'score_id':cursor.lastrowid})
    except ValueError :
        return jsonify({'success':False,
                            'error':f'Érvénytelen adatformátum hiba'}),400
    except Error as e:
        if conn and conn.is_connected():
            conn.rollback()
            cursor.close()
            conn.close()
        return jsonify({'success':False,
                        'error':f'Adatbázis hiba: {str(e)}'}),500

@app.route('/api/scores',methods=['GET'])
def get_scores():
    #Eredmények lekérése
    try:
        game_mod = request.args.get('game_mod','all')
        limit = int(request.args.get('limit',20))

        conn= get_db_connect()
        if conn is None:
            return jsonify({'success': False,
                    'error': 'Adatbázis kapcsolat hiba'}), 500
        cursor = conn.cursor(dictionary=True)
        if game_mod =='all':
            cursor.execute('''
                SELECT p.name, s.score, s.game_mod , s.game_time, s.rounds_played,s.created_at
                FROM scores s
                JOIN players p ON s.player_id=p.id
                ORDER BY s.score DESC,s.game_time ASC, s.created_at DESC
                LIMIT %s
            ''',(limit,))
        else:
            cursor.execute('''
                SELECT p.name,s.score, s.game_mod, s.game_time, s.rounds_played,s.created_at
                FROM scores s
                JOIN players p ON s.player_id=p.id
                WHERE s.game_mod=%s
                ORDER BY s.score DESC,s.game_time ASC,s.created_at DESC
                LIMIT %s
            ''',(game_mod,limit))
        scores = cursor.fetchall()

        #Datetime objektumok String-é konvertálása

        for score in scores:
            if isinstance(score['created_at'],datetime):
                score['created_at'] = score['created_at'].isoformat()

        cursor.close()
        conn.close()

        return jsonify({'success':True,
                        'scores':scores,
                        'count':len(scores)})
    except Error as e:
        return jsonify({'success':False,
                        'error':f'Adatbázis hiba:{str(e)}'}),500
    except Exception as e:
        return jsonify({'success':False,
                        'error':f'Szerver hiba:{str(e)}'}),500

@app.errorhandler(404)
def page_not_found(e):
    return jsonify({'success':False,
                    'error':'A kért erőforrás nem található'}),404
@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({'success':False,
                    'error':'Belső szerver hiba'}),500

@app.route('/api/players',methods=['GET'])
def get_players():
    try:
        conn= get_db_connect()
        if conn is None:
            return jsonify({'success':False,
                            'error':'Adatbázis kapcsolat hiba'}),500
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT p.id, p.name, p.last_played,COUNT(s.id) as games_played,MAX(s.score) as best_score 
            FROM players p
            LEFT JOIN scores s ON s.player_id=p.id
            GROUP BY p.id
            ORDER BY p.last_played DESC
        ''')
        players = cursor.fetchall()
        cursor.close()
        conn.close()

        return jsonify({'success':True,
                        'players':players})
    except Error as e:
        return jsonify({'success':False,
                    'error':f'Adatbázis hiba:{str(e)}'}),500


if __name__ == '__main__':
    print("Adatbázis inicializálása")
    init_db()
    print("Flask inditása")
    app.run(debug=True, host='0.0.0.0', port=5000)