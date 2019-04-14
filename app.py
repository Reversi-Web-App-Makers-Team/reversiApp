import sqlite3

from flask import Flask
from flask import g
from flask import render_template
from flask import request
from reversiTools.web_app_reversi_tools import get_dqn_move
from reversiTools.web_app_reversi_tools import get_initial_status
from reversiTools.web_app_reversi_tools import get_simple_board
from reversiTools.web_app_reversi_tools import intlist2strings
from reversiTools.web_app_reversi_tools import list2matrix
from reversiTools.web_app_reversi_tools import step
from reversiTools.web_app_reversi_tools import strings2intlist
from reversiTools.web_app_reversi_tools import intlist2symbol_list
from reversiTools.web_app_reversi_tools import inc_list

from sqlite3_commands import CREATE_BOARD_INFO_TABLE
from sqlite3_commands import CREATE_PLAYER_NAME_TABLE
from sqlite3_commands import GET_BOARD_INFO
from sqlite3_commands import GET_NEXT_TURN
from sqlite3_commands import GET_PLAYER_BLACK_NAME
from sqlite3_commands import GET_PLAYER_COLOR
from sqlite3_commands import GET_PLAYER_WHITE_NAME
from sqlite3_commands import REGISTER_BOARD_INFO
from sqlite3_commands import REGISTER_PLAYER_BLACK_NAME
from sqlite3_commands import REGISTER_PLAYER_WHITE_NAME
from sqlite3_commands import UPDATE_BOARD_INFO

app = Flask(__name__)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('reversi.db')
    return db


'''
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
'''

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/home/')
def home():
    return render_template('home.html')


@app.route('/mode_select', methods=['POST'])
def mode_select():
    db = get_db()
    curs = db.cursor()

    username = request.form["username"]
    board_list_with_2, player_color = get_initial_status()
    board_list_with_2_strings = intlist2strings(board_list_with_2)

    curs.execute(CREATE_PLAYER_NAME_TABLE)

    if player_color == 1:
        curs.execute(REGISTER_PLAYER_WHITE_NAME, (username,))
    else:
        curs.execute(REGISTER_PLAYER_BLACK_NAME, (username,))

    curs.execute(CREATE_BOARD_INFO_TABLE)
    curs.execute(REGISTER_BOARD_INFO, (board_list_with_2_strings, -1))

    db.commit()
    curs.close()

    return render_template('mode_select.html')


@app.route('/game/dqn', methods=['POST'])
@app.route('/game/dqn/<index>', methods=['GET'])
def dqn(index=None):
    db = get_db()
    curs = db.cursor()

    # initialize game
    if request.method == 'POST':
        curs.execute(GET_PLAYER_COLOR)
        dqn_color = -1 * curs.fetchone()[0]
        curs.execute(GET_BOARD_INFO)
        board_list_with_2 = strings2intlist(curs.fetchone()[0])

        # player is black player (player plays first turn)
        if dqn_color == 1:
            curs.execute(REGISTER_PLAYER_WHITE_NAME, ('DQN',))
            winner = 0

        # dqn is black player (dqn plays first turn)
        else:
            curs.execute(REGISTER_PLAYER_BLACK_NAME, ('DQN',))
            # play first turn
            curs.execute(GET_NEXT_TURN)
            next_turn = curs.fetchone()[0]
            next_index = get_dqn_move(board_list_with_2, next_turn)
            board_list_with_2, next_turn, winner = \
                step(board_list_with_2, next_index, next_turn)
            board_list_with_2_strings = intlist2strings(board_list_with_2)
            curs.execute(UPDATE_BOARD_INFO,
                         (board_list_with_2_strings, next_turn)
                         )

        board_list, putable_pos = get_simple_board(board_list_with_2)
        symbol_list = intlist2symbol_list(board_list)
        board_matrix = list2matrix(symbol_list)
        curs.execute(GET_PLAYER_BLACK_NAME)
        black_player = curs.fetchone()[0]
        curs.execute(GET_PLAYER_WHITE_NAME)
        white_player = curs.fetchone()[0]

        db.commit()
        curs.close()

        return render_template(
            'dqn.html',
            black_player=black_player,
            white_player=white_player,
            board_matrix=board_matrix,
            putable_pos=inc_list(putable_pos),
            winner=winner
        )

    # player put stone (method=='get')
    else:
        index = request.args["index"] - 1
        curs.execute(GET_BOARD_INFO)
        board_list_with_2 = strings2intlist(curs.fetchone()[0])
        curs.execute(GET_NEXT_TURN)
        next_turn = curs.fetchone()[0]
        curs.execute(GET_PLAYER_BLACK_NAME)
        black_player = curs.fetchone()[0]
        curs.execute(GET_PLAYER_WHITE_NAME)
        white_player = curs.fetchone()[0]
        # put stone at index and update board (play player turn)
        board_list_with_2, next_turn, winner = \
            step(board_list_with_2, index, next_turn)
        board_list_with_2_strings = intlist2strings(board_list_with_2)
        curs.execute(UPDATE_BOARD_INFO,
                     (board_list_with_2_strings, next_turn)
                     )

        while True:
            # it's DQN turn
            if (next_turn == 1 and white_player == 'DQN') or \
                    (next_turn == -1 and black_player == 'DQN'):
                next_index = get_dqn_move(board_list_with_2, next_turn)
                board_list_with_2, next_turn, winner = \
                    step(board_list_with_2, next_index, next_turn)
                board_list_with_2_strings = intlist2strings(board_list_with_2)
                curs.execute(UPDATE_BOARD_INFO,
                             (board_list_with_2_strings, next_turn)
                             )
                #TODO -> nishimoto: make case if game finishes with dqn move.

            # it's player's turn (ask put index again)
            else:
                db.commit()
                curs.close()

                board_list, putable_pos = get_simple_board(board_list_with_2)
                symbol_list = intlist2symbol_list(board_list)
                board_matrix = list2matrix(symbol_list)

                return render_template(
                    'dqn.html',
                    black_player=black_player,
                    white_player=white_player,
                    board_matrix=board_matrix,
                    putable_pos=inc_list(putable_pos),
                    winner=winner
                )


@app.route('/fin', methods=['POST'])
def fin():
    winner = request.form["winner"]
    return render_template('fin.html', winner=winner)


def _main():
    app.run(debug=True)


if __name__ == '__main__':
    _main()
