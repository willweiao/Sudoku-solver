import tkinter as tk
import copy
from copy import deepcopy
from core.generator import generate_puzzle
from core.logical_hints import get_all_hints
from core.checker import compare_with_solution
from utils.helpers import is_grid_full
from core.solver import solve_sudoku
from core.logical_hints import get_candidates

#puzzle = generate_puzzle(clues=30)
puzzle=[
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
solution = solve_sudoku(deepcopy(puzzle))

# ensure that the generated puzzle does have a solution
if solution is None:
    print("The Generated Puzzle is unsolvable, please regenerate!")

grid = [[puzzle[i][j] for j in range(9)] for i in range(9)]
candidates = [[set() for _ in range(9)] for _ in range(9)]

font_big = ("Helvetica", 18)
font_small = ("Arial", 7)

def launch_ui():
    root = tk.Tk()
    root.title("数独解题辅助")

    entries = [[None for _ in range(9)] for _ in range(9)]
    frame = tk.Frame(root)
    frame.grid(row=0, column=0, padx=10, pady=10)

    def on_input(i, j):
        val = entries[i][j].get()
        val = "".join(sorted(set(c for c in val if c in "123456789")))
        entries[i][j].delete(0, tk.END)
        entries[i][j].insert(0, val)

        if len(val) == 1:
            grid[i][j] = int(val)
            candidates[i][j] = set()
            entries[i][j].config(font=font_big, fg="black", justify="center", bg="white")
        elif len(val) > 1:
            grid[i][j] = None
            candidates[i][j] = set(val)
            entries[i][j].config(font=font_small, fg="gray", justify="left", bg="white")
        else:
            grid[i][j] = None
            candidates[i][j] = set()
            entries[i][j].config(font=font_big, fg="black", justify="center", bg="white")
    
    
    def show_hint():
        if is_grid_full(grid):
            errors = compare_with_solution(grid, solution)
            if not errors:
                status_label.config(text="🎉 恭喜你完成数独！")
            else:
                for (i, j) in errors:
                    entries[i][j].config(bg="#fdd")
                status_label.config(text="❌ 有错误，请检查红色格子")
        else:
            # Step 1: 检查用户填写的确定数字是否正确
            wrong_digits = []
            for i in range(9):
                for j in range(9):
                    if puzzle[i][j] is None and grid[i][j] is not None:
                        if grid[i][j] != solution[i][j]:
                            wrong_digits.append((i, j))
                            entries[i][j].config(bg="#fdd")

            if wrong_digits:
                status_label.config(text="❌ 有错误的确定数字，请检查红色格子")
                return  # 不再继续检查候选数
            
            # 检查用户填写的候选数是否包含错误项（和系统候选冲突）
            system_candidates = get_candidates(grid)
            invalid = []
            hint_msgs = []
            for i in range(9):
                for j in range(9):
                    if not candidates[i][j]:
                        continue
                    user_cand = set(map(int, candidates[i][j]))
                    system_cand=system_candidates.get((i, j), set())
                    if user_cand != system_cand:
                        invalid.append((i, j))
                        entries[i][j].config(bg="#fdd")
                        hint_msgs.append(f"格子({i+1},{j+1}) 的候选数应为: {sorted(system_cand)}")
            if invalid:
                status_label.config(text="⚠️ 有不合法候选数！\n" + "\n".join(hint_msgs))
                return
            
            hints = get_all_hints(grid)
            if hints:
                best_hint = hints[0]
                status_label.config(text=f"🔍 技巧: {best_hint['technique']}\n原因: {best_hint['reason']}")
                for (i, j) in best_hint.get("eliminate_from", []) + best_hint.get("optimize", []):
                    entries[i][j].config(bg="#cce")
            else:
                status_label.config(text="🟦 当前没有可用的逻辑提示")

    for i in range(9):
        for j in range(9):
            frame.grid_rowconfigure(i, minsize=48)
            frame.grid_columnconfigure(j, minsize=48)
            if puzzle[i][j] is not None:
                label = tk.Label(frame, text=str(puzzle[i][j]), font=font_big,
                                 width=2, height=1, relief="solid", bg="#f0f0f0")
                label.grid(row=i, column=j, sticky="nsew")
            else:
                entry = tk.Entry(frame, font=font_big, width=2, justify='center')
                entry.grid(row=i, column=j, sticky="nsew")
                entry.bind("<KeyRelease>", lambda e, i=i, j=j: on_input(i, j))
                entries[i][j] = entry

    tk.Button(root, text="💡 提示", command=show_hint).grid(row=1, column=0, pady=10)

    tk.Button(root, text="🆕 新题", command=lambda: [root.destroy(), launch_ui()]).grid(row=3, column=0, pady=5)

    status_label = tk.Label(root, text="", font=("微软雅黑", 8), fg="blue", justify="left", anchor="w", wraplength=600)
    status_label.grid(row=11, column=0, columnspan=9, pady=5)

    root.mainloop()