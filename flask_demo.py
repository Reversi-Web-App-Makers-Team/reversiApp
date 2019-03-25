import sqlite3

from flask import Flask
from flask import render_template
from flask import request
from flask import g

from sqlite3_commands import CREATE_TABLE
from sqlite3_commands import INITIALIZE_WHITE_PLAYER_INFO
from sqlite3_commands import GET_WHITE_PLAYER_BOARD
from sqlite3_commands import UPDATE_WHITE_PLAYER_BOARD
from sqlite3_commands import INITIALIZE_BLACK_PLAYER_INFO
from sqlite3_commands import GET_WHITE_PLAYER_BOARD
from sqlite3_commands import UPDATE_BLACK_PLAYER_BOARD

app = Flask(__name__)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('game_info.db')
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    db = get_db()
    curs = db.cursor()
    cursor.exexute()
    cursor.exexute()
    cursor.exexute()
    cursor.exexute()
    return render_template('home.html')

@app.route('/mode_select/')
def mode_select(username=None):
    username = request.values['username']
    return render_template('mode_select.html', username=username)

@app.route('/game/dqn/<index>/')
def dqn():
    return render_template('dqn.html', username=username)


@app.route('/fin/')
def fin():
    return render_template('fin.html', winner="いより")


def _main():
    app.run(debug=True)

if __name__ == '__main__':
    _main()
