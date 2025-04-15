def compare_with_solution(user_grid, solution_grid):
    """
    比较用户填写的 grid 和正确解，返回错误的位置列表
    """
    errors = []
    for i in range(9):
        for j in range(9):
            user_val = user_grid[i][j]
            correct_val = solution_grid[i][j]
            if user_val is not None and user_val != correct_val:
                errors.append((i, j))
    return errors