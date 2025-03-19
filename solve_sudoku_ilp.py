# Import PuLP for Integer Linear Programming
from pulp import LpVariable, LpProblem, LpMinimize, lpSum, LpStatus, value
import pandas as pd

def solve_sudoku_ilp(board):
    """Solve Sudoku using Integer Linear Programming (ILP) with PuLP"""
    
    # Define the problem
    prob = LpProblem("Sudoku_Solver", LpMinimize)

    # Define variables: x[i][j][k] is 1 if cell (i,j) contains number k+1
    x = [[[LpVariable(f"x_{i}_{j}_{k}", cat="Binary") for k in range(9)] for j in range(9)] for i in range(9)]

    # Constraints:
    # 1. Each cell contains exactly one number (1-9)
    for i in range(9):
        for j in range(9):
            prob += lpSum(x[i][j][k] for k in range(9)) == 1

    # 2. Each number appears exactly once per row
    for i in range(9):
        for k in range(9):
            prob += lpSum(x[i][j][k] for j in range(9)) == 1

    # 3. Each number appears exactly once per column
    for j in range(9):
        for k in range(9):
            prob += lpSum(x[i][j][k] for i in range(9)) == 1

    # 4. Each number appears exactly once per 3x3 subgrid
    for box_row in range(3):
        for box_col in range(3):
            for k in range(9):
                prob += lpSum(x[i][j][k] for i in range(box_row * 3, (box_row + 1) * 3)
                                         for j in range(box_col * 3, (box_col + 1) * 3)) == 1

    # 5. Pre-filled numbers constraints
    for i in range(9):
        for j in range(9):
            if board[i][j] is not None:
                prob += x[i][j][board[i][j] - 1] == 1  # Adjust index for 1-based Sudoku numbers

    # Solve the problem
    prob.solve()

    # Check the solution status
    if LpStatus[prob.status] == "Optimal":
        # Extract the solution
        solved_board = [[None for _ in range(9)] for _ in range(9)]
        for i in range(9):
            for j in range(9):
                for k in range(9):
                    if value(x[i][j][k]) == 1:
                        solved_board[i][j] = k + 1  # Convert back to 1-based index
        return solved_board
    else:
        return None  # No solution found

