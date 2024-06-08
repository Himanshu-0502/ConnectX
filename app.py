from flask import Flask, render_template, jsonify, request, session
from agent import agent
import numpy as np
from flask_session import Session

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = 'super secret key'
Session(app)

ROW_COUNT = 7
COLUMN_COUNT = 7
IN_A_ROW = 4

def create_board():
    return np.zeros((ROW_COUNT, COLUMN_COUNT))

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid_location(board, col):
    return board[0][col] == 0

def get_next_open_row(board, col):
    for r in range(ROW_COUNT - 1, -1, -1):
        if board[r][col] == 0:
            return r

def winning_move(board, piece):
    # Check horizontal locations
    for r in range(ROW_COUNT):
        for c in range(COLUMN_COUNT - IN_A_ROW + 1):
            if all(board[r][c + i] == piece for i in range(IN_A_ROW)):
                return True

    # Check vertical locations
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - IN_A_ROW + 1):
            if all(board[r + i][c] == piece for i in range(IN_A_ROW)):
                return True

    # Check positively sloped diagonals
    for r in range(ROW_COUNT - IN_A_ROW + 1):
        for c in range(COLUMN_COUNT - IN_A_ROW + 1):
            if all(board[r + i][c + i] == piece for i in range(IN_A_ROW)):
                return True

    # Check negatively sloped diagonals
    for r in range(IN_A_ROW - 1, ROW_COUNT):
        for c in range(COLUMN_COUNT - IN_A_ROW + 1):
            if all(board[r - i][c + i] == piece for i in range(IN_A_ROW)):
                return True

    return False

@app.route('/')
def index():
    if 'board' not in session:
        session['board'] = create_board().tolist()
        session['turn'] = 0
        session['game_over'] = False
    return render_template('index.html')

@app.route('/move', methods=['POST'])
def move():
    if session['game_over']:
        return jsonify({'board': session['board'], 'turn': session['turn'], 'game_over': session['game_over']})

    col = request.json['col']
    board = np.array(session['board'])
    turn = session['turn']

    if is_valid_location(board, col):
        row = get_next_open_row(board, col)
        drop_piece(board, row, col, turn + 1)
        if winning_move(board, turn + 1):
            session['game_over'] = True
            return jsonify({'winner': turn + 1, 'board': board.tolist(), 'turn': turn, 'game_over': session['game_over']})
        session['turn'] = (turn + 1) % 2
        session['board'] = board.tolist()

    return jsonify({'board': session['board'], 'turn': session['turn'], 'game_over': session['game_over']})

@app.route('/ai_move', methods=['POST'])
def ai_move():
    if session['game_over'] or session['turn'] != 1:
        return jsonify({'board': session['board'], 'turn': session['turn'], 'game_over': session['game_over']})

    board = np.array(session['board'])
    turn = session['turn']

    obs = {'board': board.tolist(), 'mark': turn + 1}
    config = {'rows': ROW_COUNT, 'columns': COLUMN_COUNT, 'inarow': IN_A_ROW}
    col = agent(obs, config)  # Call the minimax function
    if is_valid_location(board, col):
        row = get_next_open_row(board, col)
        drop_piece(board, row, col, turn + 1)
        if winning_move(board, turn + 1):
            session['game_over'] = True
            return jsonify({'winner': turn + 1, 'board': board.tolist(), 'turn': turn, 'game_over': session['game_over']})
        session['turn'] = (turn + 1) % 2
        session['board'] = board.tolist()

    return jsonify({'board': session['board'], 'turn': session['turn'], 'game_over': session['game_over']})

@app.route('/reset', methods=['POST'])
def reset():
    session['board'] = create_board().tolist()
    session['turn'] = 0
    session['game_over'] = False
    return jsonify({'board': session['board'], 'turn': session['turn'], 'game_over': session['game_over']})

# if __name__ == '__main__':
    # app.run(debug=True)
