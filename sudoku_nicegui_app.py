from nicegui import ui

# 9x9 数独题目（None 表示空格）
sudoku_grid = [
    [9, 1, None, None, None, 7, None, None, None],
    [None, 7, None, 1, None, 3, None, None, 8],
    [6, None, None, None, None, None, 4, None, None],
    [None, None, 2, None, None, None, None, 8, None],
    [None, None, None, None, 5, None, 7, 3, 4],
    [None, None, None, None, None, None, None, 1, None],
    [3, 4, 7, 2, None, None, 8, None, None],
    [None, None, None, None, None, 9, None, 6, None],
    [None, None, None, 8, None, None, None, None, 7],
]

# 保存用户输入状态
user_grid = [[sudoku_grid[i][j] for j in range(9)] for i in range(9)]

ui.label('🧩 NiceGUI 数独游戏模板').classes('text-2xl font-bold my-4')

# 设置固定宽度网格，格子通过 aspect-ratio 保持正方形
with ui.grid(columns=9).style('gap: 0; width: 432px;'):
    for i in range(9):
        for j in range(9):
            val = sudoku_grid[i][j]
            border = (
                f'border: 1px solid #ccc;'
                f'border-top: {"2px solid black" if i % 3 == 0 else "1px solid #ccc"};'
                f'border-left: {"2px solid black" if j % 3 == 0 else "1px solid #ccc"};'
                f'border-right: {"2px solid black" if j % 3 == 2 else "1px solid #ccc"};'
                f'border-bottom: {"2px solid black" if i % 3 == 2 else "1px solid #ccc"};'
            )
            cell_style = (
                f'width: 100%; height: 100%; aspect-ratio: 1 / 1;'
                f'display: flex; align-items: center; justify-content: center;'
                f'text-align: center; font-size: 20px; {border}'
            )

            if val is not None:
                ui.label(str(val)).style(f'{cell_style}; font-weight: bold; background: #eee;')
            else:
                def make_input(i=i, j=j):
                    def handle_change(e):
                        value = e.value
                        if value.isdigit() and 1 <= int(value) <= 9:
                            user_grid[i][j] = int(value)
                        else:
                            user_grid[i][j] = None
                    return handle_change

                ui.input('', on_change=make_input()).props('maxlength=1 input-class=text-center').style(cell_style).classes('text-blue-800')

ui.run()
