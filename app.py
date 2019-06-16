import random
import sqlite3

from flask import Flask
from flask import g
from flask import render_template
from flask import request
from reversiTools.web_app_reversi_tools import count_stone
from reversiTools.web_app_reversi_tools import get_cp_move
from reversiTools.web_app_reversi_tools import get_initial_status
from reversiTools.web_app_reversi_tools import get_simple_board
from reversiTools.web_app_reversi_tools import inc_list
from reversiTools.web_app_reversi_tools import intlist2strings
from reversiTools.web_app_reversi_tools import list2matrix
from reversiTools.web_app_reversi_tools import step
from reversiTools.web_app_reversi_tools import strings2intlist

from sqlite3_commands import CREATE_BOARD_INFO_TABLE
from sqlite3_commands import CREATE_PLAYER_NAME_TABLE
from sqlite3_commands import DELETE_BOARD_INFO_TABLE
from sqlite3_commands import DELETE_PLAYER_NAME_TABLE
from sqlite3_commands import GET_AGENT_COLOR
from sqlite3_commands import GET_AGENT_NAME
from sqlite3_commands import GET_BLACK_ATTRIBUTE
from sqlite3_commands import GET_BOARD_INFO
from sqlite3_commands import GET_NEXT_TURN
from sqlite3_commands import GET_PLAYER_BLACK_NAME
from sqlite3_commands import GET_PLAYER_WHITE_NAME
from sqlite3_commands import GET_WHITE_ATTRIBUTE
from sqlite3_commands import GET_WINNER
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


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/mode_select')
def mode_select():
    return render_template('mode_select.html')


@app.route('/home', methods=['POST'])
def home():
    db = get_db()
    curs = db.cursor()
    curs.execute(DELETE_PLAYER_NAME_TABLE)
    curs.execute(CREATE_PLAYER_NAME_TABLE)

    # initialize game
    mode = request.form['mode']

    # connect  model with agent
    translate_dict = {
        'Easy': 'RANDOM',
        'Normal': 'DQN',
        'Hard': 'SL',
        'vs Human': 'human'
    }
    agent_name = translate_dict[mode]

    # human vs agent
    if agent_name != 'human':
        agent_color = random.choice([-1, 1])
        # agent is black player (agent plays first turn)
        if agent_color == -1:
            curs.execute(REGISTER_PLAYER_BLACK_NAME, (agent_name, 'agent'))

        # agent is white player (human plays first turn)
        else:
            curs.execute(REGISTER_PLAYER_WHITE_NAME, (agent_name, 'agent'))
        db.commit()
        curs.close()

        return render_template('input_name.html')

    # human vs human
    else:
        curs.close()
        db.commit()
        return render_template('input_names.html')


@app.route('/start_human_vs_agent', methods=['POST'])
@app.route('/start_human_vs_agent', methods=['GET'])
def start_human_vs_agent():
    db = get_db()
    curs = db.cursor()

    # processing input on the previous page

    # agent vs human
    if request.method == 'POST':
        username = request.form['username']
        if not username:
            username = ' '

        curs.execute(GET_AGENT_COLOR)
        agent_color = curs.fetchone()[0]

        if agent_color == -1:
            curs.execute(REGISTER_PLAYER_WHITE_NAME, (username, 'human'))
        else:
            curs.execute(REGISTER_PLAYER_BLACK_NAME, (username, 'human'))

        db.commit()
        curs.close()
    return render_template('start.html')


@app.route('/start_human_vs_human', methods=['POST'])
def start_human_vs_human():
    db = get_db()
    curs = db.cursor()

    # processing input on the previous page

    username_1 = request.form['username_1']
    username_2 = request.form['username_2']

    # human1's color (-1 or 1)
    human1_color = random.choice([-1, 1])

    # human1 is Black player
    if human1_color == -1:
        curs.execute(REGISTER_PLAYER_WHITE_NAME, (username_2, 'human'))
        curs.execute(REGISTER_PLAYER_BLACK_NAME, (username_1, 'human'))

    # human1 is White  player
    else:
        curs.execute(REGISTER_PLAYER_WHITE_NAME, (username_1, 'human'))
        curs.execute(REGISTER_PLAYER_BLACK_NAME, (username_2, 'human'))

    db.commit()
    curs.close()

    return render_template('start.html')


@app.route('/play', methods=['POST'])
@app.route('/play/<index>', methods=['GET'])
def play(index=None):
    db = get_db()
    curs = db.cursor()
    # initialize game
    if request.method == 'POST':
        # initialize table
        curs.execute(DELETE_BOARD_INFO_TABLE)
        curs.execute(CREATE_BOARD_INFO_TABLE)

        curs.execute(GET_WHITE_ATTRIBUTE)
        white_attribute = curs.fetchone()[0]

        curs.execute(GET_PLAYER_BLACK_NAME)
        black_name = curs.fetchone()[0]
        curs.execute(GET_BLACK_ATTRIBUTE)
        black_attribute = curs.fetchone()[0]
        board_list_with_2, _ = get_initial_status()
        board_list_with_2_strings = intlist2strings(board_list_with_2)
        curs.execute(REGISTER_BOARD_INFO, (board_list_with_2_strings, -1))
        curs.execute(GET_BOARD_INFO)

        # player is black player (player plays first turn)
        if black_attribute == 'human':
            next_turn = -1
            winner = 0
            valid_flag = True
        # agent is black player (agent plays first turn)
        else:
            # agent first turn
            next_turn = -1
            winner = 0
            next_index = get_cp_move(board_list_with_2, next_turn, black_name)
            board_list_with_2, next_turn, winner, valid_flag = \
                step(board_list_with_2, next_index, next_turn)
            board_list_with_2_strings = intlist2strings(board_list_with_2)
            curs.execute(UPDATE_BOARD_INFO,
                         (board_list_with_2_strings, next_turn, winner)
                         )
        _, putable_pos = get_simple_board(board_list_with_2)
        board_matrix = list2matrix(board_list_with_2)
        curs.execute(GET_PLAYER_BLACK_NAME)
        black_player = curs.fetchone()[0]
        curs.execute(GET_PLAYER_WHITE_NAME)
        white_player = curs.fetchone()[0]
        db.commit()
        curs.close()
        white_stone_num, black_stone_num = count_stone(board_list_with_2)
        return render_template(
            'play.html',
            white_stone_num=white_stone_num,
            black_stone_num=black_stone_num,
            black_player=black_player,
            white_player=white_player,
            board_matrix=board_matrix,
            putable_pos=inc_list(putable_pos),
            winner=winner,
            valid_flag=valid_flag,
            next_turn=next_turn
        )

    # player put stone (method=='get')
    else:
        # agent_nameをDBから読み込み
        curs.execute(GET_BOARD_INFO)
        board_list_with_2 = strings2intlist(curs.fetchone()[0])
        curs.execute(GET_NEXT_TURN)
        next_turn = curs.fetchone()[0]
        curs.execute(GET_PLAYER_BLACK_NAME)
        black_player = curs.fetchone()[0]
        curs.execute(GET_PLAYER_WHITE_NAME)
        white_player = curs.fetchone()[0]
        curs.execute(GET_WHITE_ATTRIBUTE)
        white_attribute = curs.fetchone()[0]
        curs.execute(GET_BLACK_ATTRIBUTE)
        black_attribute = curs.fetchone()[0]

        # put stone at index and update board (play player turn)
        if not request.args['index']:
            # Developer's birthdate'
            index = 1218
        else:
            index = int(request.args['index']) - 1

        board_list_with_2, next_turn, winner, valid_flag = \
            step(board_list_with_2, index, next_turn)
        if winner != 0:
            _, putable_pos = get_simple_board(board_list_with_2)
            board_matrix = list2matrix(board_list_with_2)
            board_list_with_2_strings = intlist2strings(board_list_with_2)
            curs.execute(UPDATE_BOARD_INFO, (board_list_with_2_strings, next_turn, winner))
            db.commit()
            curs.close()
            white_stone_num, black_stone_num = count_stone(board_list_with_2)

            return render_template(
                'play.html',
                white_stone_num=white_stone_num,
                black_stone_num=black_stone_num,
                black_player=black_player,
                white_player=white_player,
                board_matrix=board_matrix,
                putable_pos=inc_list(putable_pos),
                winner=winner,
                valid_flag=valid_flag,
                next_turn=next_turn
            )

        board_list_with_2_strings = intlist2strings(board_list_with_2)
        curs.execute(UPDATE_BOARD_INFO,
                     (board_list_with_2_strings, next_turn, winner)
                     )

        while True:
            # it's agent turn
            if (next_turn == 1 and white_attribute == "agent") or \
                    (next_turn == -1 and black_attribute == "agent"):
                curs.execute(GET_AGENT_NAME)
                agent_name = curs.fetchone()[0]
                next_index = get_cp_move(board_list_with_2, next_turn, agent_name)
                board_list_with_2, next_turn, winner, valid_flag = \
                    step(board_list_with_2, next_index, next_turn)

                if winner != 0:
                    _, putable_pos = get_simple_board(board_list_with_2)
                    board_matrix = list2matrix(board_list_with_2)
                    board_list_with_2_strings = intlist2strings(board_list_with_2)
                    curs.execute(UPDATE_BOARD_INFO, (board_list_with_2_strings, next_turn, winner))
                    db.commit()
                    curs.close()
                    white_stone_num, black_stone_num = count_stone(board_list_with_2)

                    return render_template(
                        'play.html',
                        white_stone_num=white_stone_num,
                        black_stone_num=black_stone_num,
                        black_player=black_player,
                        white_player=white_player,
                        board_matrix=board_matrix,
                        putable_pos=inc_list(putable_pos),
                        winner=winner,
                        valid_flag=valid_flag,
                        next_turn=next_turn
                    )
                board_list_with_2_strings = intlist2strings(board_list_with_2)
                curs.execute(UPDATE_BOARD_INFO,
                             (board_list_with_2_strings, next_turn, winner)
                             )

            # it's player's turn (ask put index again)
            else:
                db.commit()
                curs.close()

                _, putable_pos = get_simple_board(board_list_with_2)
                board_matrix = list2matrix(board_list_with_2)
                white_stone_num, black_stone_num = count_stone(board_list_with_2)

                return render_template(
                    'play.html',
                    white_stone_num=white_stone_num,
                    black_stone_num=black_stone_num,
                    black_player=black_player,
                    white_player=white_player,
                    board_matrix=board_matrix,
                    putable_pos=inc_list(putable_pos),
                    winner=winner,
                    valid_flag=valid_flag,
                    next_turn=next_turn
                )


@app.route('/fin', methods=['POST'])
def fin():
    db = get_db()
    curs = db.cursor()
    curs.execute(GET_WINNER)
    winner = curs.fetchone()[0]
    if winner == 1:
        curs.execute(GET_PLAYER_WHITE_NAME)
        name = curs.fetchone()[0]
    elif winner == -1:
        curs.execute(GET_PLAYER_BLACK_NAME)
        name = curs.fetchone()[0]
    else:
        name = None
    db.commit()
    curs.close()
    return render_template(
        'fin.html',
        winner=winner,
        name=name
    )


def _main():
    app.run(debug=True, host='0.0.0.0')


if __name__ == '__main__':
    _main()
