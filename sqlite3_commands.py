CREATE_TABLE = '''
CREATE TABLE IF NOT EXISTS game_info (
color INTEGER,
username TEXT,
board TEXT
)
'''

# white == 1
INITIALIZE_WHITE_PLAYER_INFO = '''
INSERT INTO gmae_info(color, username, board) 
VALUES("1, {}, {}")
'''

GET_WHITE_PLAYER_BOARD = '''
SELECT board FROM game_info WHERE color == 1
'''

UPDATE_WHITE_PLAYER_BOARD = '''
UPDATE game_info SET {} WHERE color == 1
'''

# black == -1
INITIALIZE_BLACK_PLAYER_INFO = '''
INSERT INTO gmae_info(color, username, board) 
VALUES("-1, {}, {}")
'''

GET_BLACK_PLAYER_BOARD = '''
SELECT board FROM game_info WHERE color == -1
'''

UPDATE_BLACK_PLAYER_BOARD = '''
UPDATE game_info SET {} WHERE color == -1
'''
