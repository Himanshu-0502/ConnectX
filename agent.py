def agent(obs, config):
    import numpy as np
    import random as rd

    ROWS = config['rows']
    COLUMNS = config['columns']
    IN_A_ROW = config['inarow']

    def drop_piece(grid, col, piece):
        for row in range(ROWS - 1, -1, -1):
            if grid[row][col] == 0:
                grid[row][col] = piece
                break
        return grid

    def check_window(window, n_discs, piece):
        return (window.count(piece) == n_discs) and (window.count(0) == IN_A_ROW - n_discs)

    def count_windows(grid, n_discs, piece):
        n_windows = 0

        for row in range(ROWS):
            for col in range(COLUMNS - IN_A_ROW + 1):
                window = list(grid[row, col: col + IN_A_ROW])
                if check_window(window, n_discs, piece):
                    n_windows += 1

        for row in range(ROWS - IN_A_ROW + 1):
            for col in range(COLUMNS):
                window = list(grid[row: row + IN_A_ROW, col])
                if check_window(window, n_discs, piece):
                    n_windows += 1

        for row in range(ROWS - IN_A_ROW + 1):
            for col in range(COLUMNS - IN_A_ROW + 1):
                window = list(grid[range(row, row + IN_A_ROW), range(col, col + IN_A_ROW)])
                if check_window(window, n_discs, piece):
                    n_windows += 1

        for row in range(IN_A_ROW - 1, ROWS):
            for col in range(COLUMNS - IN_A_ROW + 1):
                window = list(grid[range(row, row - IN_A_ROW, -1), range(col, col + IN_A_ROW)])
                if check_window(window, n_discs, piece):
                    n_windows += 1

        return n_windows

    def get_heuristic(grid, piece):
        score = 0
        opp_piece = (piece % 2) + 1

        score += 1e6 * count_windows(grid, IN_A_ROW, piece)
        score += 1 * count_windows(grid, IN_A_ROW - 1, piece)
        score -= 1e4 * count_windows(grid, IN_A_ROW, opp_piece)
        score -= 1e2 * count_windows(grid, IN_A_ROW - 1, opp_piece)

        return score

    def score_move(grid, col, piece, n_steps):
        next_grid = drop_piece(grid.copy(), col, piece)
        return minimax(next_grid, n_steps - 1, False, piece, -np.Inf, np.Inf)

    def is_terminal_window(window):
        return (window.count(1) == IN_A_ROW) or (window.count(2) == IN_A_ROW)

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

    def minimax(grid, depth, maximizing_player, piece, alpha, beta):
        is_terminal = is_terminal_grid(grid)
        valid_moves = [col for col in range(COLUMNS) if grid[0][col] == 0]

        if depth == 0 or is_terminal:
            return get_heuristic(grid, piece)

        if maximizing_player:
            max_eval = -np.Inf
            for col in valid_moves:
                child = drop_piece(grid.copy(), col, piece)
                eval = minimax(child, depth - 1, False, piece, alpha, beta)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if alpha >= beta:
                    break
            return max_eval
        else:
            min_eval = np.Inf
            opp_piece = (piece % 2) + 1
            for col in valid_moves:
                child = drop_piece(grid.copy(), col, opp_piece)
                eval = minimax(child, depth - 1, True, piece, alpha, beta)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if alpha >= beta:
                    break
            return min_eval

    def play():
        grid = np.array(obs['board']).reshape(ROWS, COLUMNS)
        piece = obs['mark']
        valid_moves = [col for col in range(COLUMNS) if grid[0][col] == 0]

        n_steps = 3
        scores = {col: score_move(grid, col, piece, n_steps) for col in valid_moves}
        max_score = max(scores.values())
        best_cols = [col for col in valid_moves if scores[col] == max_score]
        return rd.choice(best_cols)

    return play()