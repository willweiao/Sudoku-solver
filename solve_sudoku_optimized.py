import numpy as np

def get_candidates(board):
    """Compute possible candidates for each empty cell in the Sudoku board."""
    candidates_dict = {}

    def is_valid(board, row, col, num):
        """Check if num can be placed at (row, col)."""
        for i in range(9):
            if board[row][i] == num or board[i][col] == num:
                return False
        # Compute the 3x3 subgrid start indices
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                if board[start_row + i][start_col + j] == num:
                    return False
        return True

    # Compute candidates for each empty cell
    for row in range(9):
        for col in range(9):
            if board[row][col] is None:  # Only process empty cells
                possible_numbers = {num for num in range(1, 10) if is_valid(board, row, col, num)}
                candidates_dict[(row, col)] = possible_numbers

    return candidates_dict

def auto_fill_single_candidates(board):
    """Automatically fills in sole candidates in the Sudoku board using Constraint Propagation."""
    changed = True  # Flag to track if changes occur

    while changed:
        changed = False
        candidates = get_candidates(board)

        for (row, col), possible_values in candidates.items():
            if len(possible_values) == 1:  # If only one candidate exists, fill it in
                board[row][col] = possible_values.pop()
                changed = True  # Mark change occurred

    return board

def find_best_empty_cell(candidates_dict):
    """Find the empty cell with the fewest candidates (Minimum Remaining Values - MRV)."""
    return min(candidates_dict, key=lambda pos: len(candidates_dict[pos]))

def solve_sudoku_optimized(board):
    """Solves Sudoku using Constraint Propagation and Backtracking."""
    board = auto_fill_single_candidates(board)  # Apply Constraint Propagation
    candidates_dict = get_candidates(board)  # Get updated candidates after pre-filling

    if not candidates_dict:
        return True  # Sudoku is already solved

    # Find the empty cell with the fewest candidates (MRV heuristic)
    row, col = find_best_empty_cell(candidates_dict)

    for num in sorted(candidates_dict[(row, col)]):  # Try numbers in ascending order
        board[row][col] = num  # Place the number
        if solve_sudoku_optimized(board):  # Recursive call
            return True
        board[row][col] = None  # Backtrack

    return False  # No solution found

def print_sudoku(board):
    """Prints the Sudoku grid in a readable format."""
    for row in board:
        print(" ".join(str(num) if num is not None else "." for num in row))

# Example Sudoku puzzle (0 or None represents empty spaces)
sudoku_board = [
    [None, 2, None, 6, None, 8, None, None, None],
    [5, 8, None, None, None, 9, 7, None, None],
    [None, None, None, None, 4, None, None, None, None],
    [3, 7, None, None, None, None, 5, None, None],
    [6, None, None, None, None, None, None, None, 4],
    [None, None, 8, None, None, None, None, 1, 3],
    [None, None, None, None, 2, None, None, None, None],
    [None, None, 9, 8, None, None, None, 3, 6],
    [None, None, None, 3, None, 6, None, 9, None],
]

print("Original Sudoku:")
print_sudoku(sudoku_board)

if solve_sudoku_optimized(sudoku_board):
    print("\nSolved Sudoku:")
    print_sudoku(sudoku_board)
else:
    print("No solution exists.")
