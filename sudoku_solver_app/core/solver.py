"""
This is the sudoku solver using back tracking method. The purpose of this file
is solve the given sudoku puzzle and give the only correct answer. It's not 
about the logical inference or any methods that we use in solving a sudoku 
puzzle manually. The advantage of using it is its efficiency and correctness.
Later on we will need this answer to check if the user made every position
that already filled correctly. If so, then we can give a possible hint. If not,
then we need to point out where it is wrongly considered, instead of giving a
hint on the wrong step.
"""


def is_valid(board, row, col, num):
    """Check if placing 'num' at (row, col) follows Sudoku rules."""
    # Check row
    if num in board[row]:
        return False
    # Check column
    if num in [board[i][col] for i in range(9)]:
        return False
    # Check 3x3 subgrid
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def find_empty_cell(board):
    """Find the next empty cell (returns (row, col)), or None if the board is full."""
    for row in range(9):
        for col in range(9):
            if board[row][col] is None or board[row][col] == 0:
                return row, col
    return None

def solve_sudoku(board):
    """Solve the Sudoku puzzle using backtracking."""
    empty_cell = find_empty_cell(board)
    if not empty_cell:
        return board  # Puzzle solved

    row, col = empty_cell
    for num in range(1, 10):  # Try numbers 1-9
        if is_valid(board, row, col, num):
            board[row][col] = num  # Place the number
            result = solve_sudoku(board)
            if result:
                return result
            board[row][col] = None  # Backtrack

    return None  # No solution found