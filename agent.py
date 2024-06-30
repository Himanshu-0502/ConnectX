def agent(obs, config):
    # Import required libraries
    import numpy as np
    import time

    # Transposition table to store the heuristic scores of the states
    transposition_table = {}

    # Constants
    ROWS = config['rows']
    COLUMNS = config['columns']
    IN_A_ROW = config['inarow']
    TIME_LIMIT = 10.0

    # Function to drop a piece into the grid
    def drop_piece(grid, col, piece):
        for row in range(ROWS - 1, -1, -1):
            if grid[row][col] == 0:
                grid[row][col] = piece
                break
        return grid

    # Function to check if a window meets the criteria
    def check_window(window, discs, piece):
        return (window.count(piece) == discs) and (window.count(0) == IN_A_ROW - discs)

    # Function to count the number of valid windows in the grid
    def count_windows(grid, discs, piece):
        n_windows = 0

        # Horizontal windows
        for row in range(ROWS):
            for col in range(COLUMNS - IN_A_ROW + 1):
                window = list(grid[row, col: col + IN_A_ROW])
                if check_window(window, discs, piece):
                    n_windows += 1

        # Vertical windows
        for row in range(ROWS - IN_A_ROW + 1):
            for col in range(COLUMNS):
                window = list(grid[row: row + IN_A_ROW, col])
                if check_window(window, discs, piece):
                    n_windows += 1

        # Positive diagonal windows
        for row in range(ROWS - IN_A_ROW + 1):
            for col in range(COLUMNS - IN_A_ROW + 1):
                window = list(grid[range(row, row + IN_A_ROW), range(col, col + IN_A_ROW)])
                if check_window(window, discs, piece):
                    n_windows += 1

        # Negative diagonal windows
        for row in range(IN_A_ROW - 1, ROWS):
            for col in range(COLUMNS - IN_A_ROW + 1):
                window = list(grid[range(row, row - IN_A_ROW, -1), range(col, col + IN_A_ROW)])
                if check_window(window, discs, piece):
                    n_windows += 1

        return n_windows

    # Function to calculate the heuristic score of the grid
    def get_heuristic(grid, piece):
        score = 0
        opp_piece = (piece % 2) + 1

        score += 1e9 * count_windows(grid, IN_A_ROW - 0, piece)
        score -= 1e6 * count_windows(grid, IN_A_ROW - 0, opp_piece)
        score += 1e3 * count_windows(grid, IN_A_ROW - 1, piece)
        score -= 1e0 * count_windows(grid, IN_A_ROW - 1, opp_piece)

        return score

    # Function to score a potential move
    def score_move(grid, col, piece, steps):
        next_grid = drop_piece(grid.copy(), col, piece)
        return minimax(next_grid, steps - 1, False, piece, -np.Inf, np.Inf)

    # Function to check if a window is terminal (winning)
    def is_terminal_window(window):
        return (window.count(1) == IN_A_ROW) or (window.count(2) == IN_A_ROW)

    # Function to check if the grid is in a terminal state
    def is_terminal_grid(grid):
        if 0 not in grid[0]:
            return True

        for row in range(ROWS):
            for col in range(COLUMNS - IN_A_ROW + 1):
                if is_terminal_window(list(grid[row, col: col + IN_A_ROW])):
                    return True

        for row in range(ROWS - IN_A_ROW + 1):
            for col in range(COLUMNS):
                if is_terminal_window(list(grid[row: row + IN_A_ROW, col])):
                    return True

        for row in range(ROWS - IN_A_ROW + 1):
            for col in range(COLUMNS - IN_A_ROW + 1):
                if is_terminal_window(list(grid[range(row, row + IN_A_ROW), range(col, col + IN_A_ROW)])):
                    return True

        for row in range(IN_A_ROW - 1, ROWS):
            for col in range(COLUMNS - IN_A_ROW + 1):
                if is_terminal_window(list(grid[range(row, row - IN_A_ROW, -1), range(col, col + IN_A_ROW)])):
                    return True

        return False

    # Minimax algorithm with alpha-beta pruning and move ordering
    def minimax(grid, depth, maximizing_player, piece, alpha, beta):
        state_key = grid.tobytes()
        if state_key in transposition_table:
            return transposition_table[state_key]

        if depth == 0 or is_terminal_grid(grid):
            score = get_heuristic(grid, piece)
            transposition_table[state_key] = score
            return score

        valid_moves = [col for col in range(COLUMNS) if grid[0][col] == 0]

        if maximizing_player:
            max_eval = -np.Inf
            for col in valid_moves:
                child = drop_piece(grid.copy(), col, piece)
                eval = minimax(child, depth - 1, False, piece, alpha, beta)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if alpha >= beta:
                    break
            transposition_table[state_key] = max_eval
            return max_eval
        else:
            min_eval = np.Inf
            for col in valid_moves:
                child = drop_piece(grid.copy(), col, (piece % 2) + 1)
                eval = minimax(child, depth - 1, True, piece, alpha, beta)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if alpha >= beta:
                    break
            transposition_table[state_key] = min_eval
            return min_eval

    # Main function to determine the best move using iterative deepening
    def play():
        grid = np.asarray(obs['board']).reshape(ROWS, COLUMNS)
        piece = obs['mark']
        valid_moves = [col for col in range(COLUMNS) if grid[0][col] == 0]

        max_depth = 1
        start_time = time.time()
        while (time.time() - start_time) * len(valid_moves) < TIME_LIMIT:
            transposition_table.clear()
            valid_moves = sorted(valid_moves, key=lambda col: score_move(grid, col, piece, max_depth), reverse=True)
            max_depth += 1

        return valid_moves[0]

    return play()