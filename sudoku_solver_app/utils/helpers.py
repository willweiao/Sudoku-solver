def is_grid_full(grid):
    """
    判断数独是否所有格子都填满（None 表示空）
    """
    return all(all(cell is not None for cell in row) for row in grid)