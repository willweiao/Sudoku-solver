import random
import copy
from core.solver import solve_sudoku

def is_valid(grid, row, col, num):
    for i in range(9):
        if grid[row][i] == num or grid[i][col] == num:
            return False
    box_row, box_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(box_row, box_row + 3):
        for j in range(box_col, box_col + 3):
            if grid[i][j] == num:
                return False
    return True

def fill_grid(grid):
    for i in range(9):
        for j in range(9):
            if grid[i][j] is None:
                nums = list(range(1, 10))
                random.shuffle(nums)
                for num in nums:
                    if is_valid(grid, i, j, num):
                        grid[i][j] = num
                        if fill_grid(grid):
                            return True
                        grid[i][j] = None
                return False
    return True

def generate_full_grid():
    grid = [[None for _ in range(9)] for _ in range(9)]
    fill_grid(grid)
    return grid

def generate_puzzle(clues=30):
    grid = generate_full_grid()
    puzzle = copy.deepcopy(grid)
    cells = [(i, j) for i in range(9) for j in range(9)]
    random.shuffle(cells)
    removed = 0
    for i, j in cells:
        backup = puzzle[i][j]
        puzzle[i][j] = None
        solution = solve_sudoku(copy.deepcopy(puzzle))
        if not solution:
            puzzle[i][j] = backup
        else:
            removed += 1
        if 81 - removed >= clues:
            continue
        else:
            break
    return puzzle