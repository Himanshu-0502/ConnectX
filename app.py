from flask import Flask, render_template, jsonify, request, session
import numpy as np
from flask_session import Session
from agent import agent

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = 'super secret key'
Session(app)

# Game configuration
ROWS = 6
COLUMNS = 7
IN_A_ROW = 4
config = {'rows': ROWS, 'columns': COLUMNS, 'inarow': IN_A_ROW}

# Game helper functions
def create_board():
    """Create a new game board."""
    return np.zeros((ROWS, COLUMNS))

# Function to drop a piece into the grid
def drop_piece(board, col, piece):
    """Drop a piece into the board."""
    for row in range(ROWS - 1, -1, -1):
        if board[row][col] == 0:
            board[row][col] = piece
            break
    return board

def is_valid_location(board, col):
    """Check if the column is a valid location for a move."""
    return board[0][col] == 0

def winning_move(board, piece):
    """Check if the last move was a winning move."""
    # Check horizontal locations
    for r in range(ROWS):
        for c in range(COLUMNS - IN_A_ROW + 1):
            if all(board[r][c + i] == piece for i in range(IN_A_ROW)):
                return True
    # Check vertical locations
    for c in range(COLUMNS):
        for r in range(ROWS - IN_A_ROW + 1):
            if all(board[r + i][c] == piece for i in range(IN_A_ROW)):
                return True
    # Check positively sloped diagonals
    for r in range(ROWS - IN_A_ROW + 1):
        for c in range(COLUMNS - IN_A_ROW + 1):
            if all(board[r + i][c + i] == piece for i in range(IN_A_ROW)):
                return True
    # Check negatively sloped diagonals
    for r in range(IN_A_ROW - 1, ROWS):
        for c in range(COLUMNS - IN_A_ROW + 1):
            if all(board[r - i][c + i] == piece for i in range(IN_A_ROW)):
                return True
    return False

@app.route('/')
def index():
    """Render the main game page."""
    if 'board' not in session:
        session['board'] = create_board().tolist()
        session['turn'] = 0
        session['game_over'] = False
    return render_template('index.html')

@app.route('/move', methods=['POST'])
def player_move():
    """Handle a player's move."""
    if session['game_over']:
        return jsonify({'board': session['board'], 'turn': session['turn'], 'game_over': session['game_over']})

    board = np.array(session['board'])
    turn = session['turn']
    col = request.json['col'] # Get player move

    if is_valid_location(board, col):
        drop_piece(board, col, turn + 1)
        if winning_move(board, turn + 1):
            session['game_over'] = True
            return jsonify({'winner': turn + 1, 'board': board.tolist(), 'turn': turn, 'game_over': session['game_over']})
        session['turn'] = (turn + 1) % 2
        session['board'] = board.tolist()

    return jsonify({'board': session['board'], 'turn': session['turn'], 'game_over': session['game_over']})

@app.route('/ai_move', methods=['POST'])
def agent_move():
    """Handle the agent's move."""
    if session['game_over'] or session['turn'] != 1:
        return jsonify({'board': session['board'], 'turn': session['turn'], 'game_over': session['game_over']})

    board = np.array(session['board'])
    turn = session['turn']
    col = agent({'board': board.flatten(), 'mark': turn + 1}, config)  # Get agent move

    if is_valid_location(board, col):
        drop_piece(board, col, turn + 1)
        if winning_move(board, turn + 1):
            session['game_over'] = True
            return jsonify({'winner': 2, 'board': board.tolist(), 'turn': session['turn'], 'game_over': session['game_over']})
        session['turn'] = (session['turn'] + 1) % 2
        session['board'] = board.tolist()

    return jsonify({'board': session['board'], 'turn': session['turn'], 'game_over': session['game_over']})

@app.route('/reset', methods=['POST'])
def reset():
    """Reset the game to its initial state."""
    session['board'] = create_board().tolist()
    session['turn'] = 0
    session['game_over'] = False
    return jsonify({'board': session['board'], 'turn': session['turn'], 'game_over': session['game_over']})

# if __name__ == '__main__':
#     app.run(debug=True)
