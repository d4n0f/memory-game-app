from flask import Flask, render_template, request
import mysql.connector
from mysql.connector import Error

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


if __name__ == '__main__':
    print("Flask inditása")
    app.run(debug=True, host='0.0.0.0', port=5000)