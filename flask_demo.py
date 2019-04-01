import sqlite3
import numpy as np
from flask import Flask
from flask import render_template
from flask import request, session
from flask import g

from reversiTools.web_app_reversi_tools import intlist2strings
from reversiTools.web_app_reversi_tools import strings2intlist
from reversiTools.web_app_reversi_tools import list2matrix
from reversiTools.web_app_reversi_tools import matrix2list
from reversiTools.web_app_reversi_tools import get_simple_board
from reversiTools.web_app_reversi_tools import get_initial_status
from reversiTools.web_app_reversi_tools import step
from sqlite3_commands import CREATE_PLAYER_NAME_TABLE
from sqlite3_commands import REGISTER_PLAYER_WHITE_NAME 
from sqlite3_commands import GET_PLAYER_WHITE_NAME
from sqlite3_commands import REGISTER_PLAYER_BLACK_NAME
from sqlite3_commands import GET_PLAYER_BLACK_NAME
from sqlite3_commands import CREATE_BOARD_INFO_TABLE
from sqlite3_commands import REGISTER_BOARD_INFO
from sqlite3_commands import GET_BOARD_INFO
from sqlite3_commands import UPDATE_BOARD_INFO 


app = Flask(__name__)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('reversi.db')
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
         db.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home/') 
def home():
    # db = get_db()
    # curs = db.cursor()
    
    # player_name = request.form["username"]
    # "board_filled_with_2, player_color = get_initial_status()
    # board_filled_with_2_strings = intlist2string(board_filled_with_2)

    # curs.exexute(CREATE_NAME_TABLE)

    # if player_color == 1:
    #     curs.execute(REGISTER_PLAYER_WHITE_NAME.format(player_name))

    # elif player_color == -1:
    #    curs.execute(REGISTER_PLAYER_BLACK_NAME.format(player_name))

    # cusr.execute(CREATE_BOARD_INFO_TABLE)
    # curs.execute(REGISTER_BOARD_INFO.format(board_filled_with_2_strings))

    # db.commit()
    # curs.close()

    return render_template('home.html')

@app.route('/mode_select/')
def mode_select():
    username = request.values["username"]
    print(username)
    return render_template('mode_select.html')

@app.route('/game/dqn/')
def dqn():
    mat = np.zeros((8,8)).tolist()
    return render_template('dqn.html', black_player="いより", white_player="dqn", Board_Matrix=[mat])


@app.route('/fin/', methods=["GET"])
def fin():
    return render_template('fin.html', winner="いより")

def _main():
    app.run(debug=True)

if __name__ == '__main__':
    _main()
