import random
import copy
from copy import deepcopy
# from solver import solve_sudoku
from logical_hints import get_all_hints
# from collections import Counter


# 可用的技巧列表
TECHNIQUE_SCORES = {
    "Naked Single": 1,
    "Hidden Single": 1,
    "Naked Subset (2)": 2,
    "Hidden Subset (2)": 2,
    "Pointing": 2,
    "Claiming": 2,
    "Naked Subset (3)": 3,
    "Hidden Subset (3)": 3,
    "Naked Subset (4)": 3,
    "Hidden Subset (4)": 3,
    "X-Wing": 4,
    "Naked Subset (5)": 4,
    "Hidden Subset (5)": 4,
    "Naked Subset (6)": 4,
    "Hidden Subset (6)": 4,
    "Naked Subset (7)": 4,
    "Hidden Subset (7)": 4,
    "Naked Subset (8)": 4,
    "Hidden Subset (8)": 4,
    "Swordfish": 5,
    "XY-Wing": 5,
}

# 设计的难度等级
LEVEL_SETTINGS = {
    "Easy": (30, 40),
    "Medium": (40, 50),
    "Hard": (50, 60),
    "Extreme": (55, 60),
}


def evaluate_logical_difficulty(hints):
    """根据逻辑hint使用情况综合计算复杂度得分，仅看easy,medium,hard三个难度"""
    score = 0
    highest_score = 0
    for hint in hints:
        tech = hint.get("technique", "")
        technique_score = TECHNIQUE_SCORES.get(tech, 5)  # 未知技巧算高难度
        score += technique_score
        highest_score = max(highest_score, technique_score)
    return score, highest_score


# 评估数独题目的难度：包括holes以及max tech level
def evaluate_puzzle_difficulty(puzzle):

    num_holes = sum(1 for row in puzzle for cell in row if cell is None)
    hints = get_all_hints(puzzle)
    
    score, max_tech_level = evaluate_logical_difficulty(hints)
    simple_hints = [hint for hint in hints if hint.get("technique") in ("Naked Single", "Hidden Single")]

    # 特别判断Extreme ：分数非常高 或 50+空且简单hint极少
    if (score >= 80) or (num_holes >= 50 and len(simple_hints) <= 3):
        return "Extreme"

    if not simple_hints:
        return "Extreme"
    
    logic_score, max_tech_level = evaluate_logical_difficulty(hints)

    # 综合判定
    if num_holes <= 40 and max_tech_level <= 2:
        return "Easy"
    elif num_holes <= 50 and max_tech_level <= 3:
        return "Medium"
    else :
        return "Hard"
    

def generate_full_board():
    """Generate a fully filled Sudoku board"""
    board = [[None for _ in range(9)] for _ in range(9)]
    numbers = list(range(1, 10))
    def fill(board):
        empty = next(((i, j) for i in range(9) for j in range(9) if board[i][j] is None), None)
        if not empty:
            return True
        i, j = empty
        random.shuffle(numbers)
        for num in numbers:
            if is_valid(board, i, j, num):
                board[i][j] = num
                if fill(board):
                    return True
                board[i][j] = None
        return False

    fill(board)
    return board


def is_valid(board, row, col, num):
    """Check if a number can be placed at (row, col)"""
    if num in board[row]:
        return False
    if num in (board[i][col] for i in range(9)):
        return False
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True


def has_unique_solution(board):
    """Check whether the board has a unique solution"""
    solutions = []

    def solve(board):
        empty = next(((i, j) for i in range(9) for j in range(9) if board[i][j] is None), None)
        if not empty:
            solutions.append(deepcopy(board))
            return len(solutions) < 2  # Stop once two solutions are found

        i, j = empty
        for num in range(1, 10):
            if is_valid(board, i, j, num):
                board[i][j] = num
                if not solve(board):
                    board[i][j] = None
                    return False
                board[i][j] = None
        return True

    solve(deepcopy(board))
    return len(solutions) == 1


def generate_puzzle(num_holes):
    """Generate a Sudoku puzzle with a specified number of holes, ensuring a unique solution"""
    full_board = generate_full_board()
    puzzle = deepcopy(full_board)
    cells = [(i, j) for i in range(9) for j in range(9)]
    random.shuffle(cells)
    removed = 0

    for i, j in cells:
        temp = puzzle[i][j]
        puzzle[i][j] = None
        if not has_unique_solution(puzzle):
            puzzle[i][j] = temp
        else:
            removed += 1
            if removed >= num_holes:
                break

    return puzzle, full_board


# 生成在目标难度下的数独题
def generate_puzzle_by_level(level):
    """Generate a puzzle by specified difficulty (Easy, Medium, Hard, Extreme)"""
    assert level in LEVEL_SETTINGS, "Invalid level."

    min_holes, max_holes = LEVEL_SETTINGS[level]

    attempts = 0

    while attempts < 500:  # 最多尝试500次
        num_holes = random.randint(min_holes, max_holes)
        puzzle, solution = generate_puzzle(num_holes)
        difficulty = evaluate_puzzle_difficulty(puzzle)

        if difficulty == level:
            return puzzle, solution, difficulty
        
        attempts += 1

    # 如果500次还没找到，返回最后一次生成的
    print(f"Warning: Couldn't generate {level} level after {attempts} tries, returning closest match.")
    
    return puzzle, solution, difficulty