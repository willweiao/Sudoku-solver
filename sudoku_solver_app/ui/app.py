import tkinter as tk
import copy
import json
from copy import deepcopy
import tkinter.messagebox as messagebox
from core.generator import generate_puzzle_by_level
from core.logical_hints import get_all_hints
from core.checker import compare_with_solution
from utils.helpers import is_grid_full
from core.solver import solve_sudoku
from core.logical_hints import get_candidates


"""
# use a fixed puzzle to check the code
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
"""
# all the colors used
COLORS = {
    "background_white": "#ffffff",     # 普通格子
    "background_gray": "#f0f0f0",      # 交错宫格背景
    "highlight": "#ccf",               # 点击高亮行列宫格
    "hint": "#d4edda",                 # 提示高亮
    "error": "#fdd",                   # 错误格子
    "hint_text_fg": "blue",            # 提示栏文字
}

# global font
font_big = ("Helvetica", 18)
font_small = ("Arial", 7)

# timer initialize
elapsed_time = 0        # 已经计时的秒数
is_paused = False       # 当前是否处于暂停状态
timer_label = None      # 显示用的标签
overlay_frame = None    # 暂停时的遮罩层

# input grid function
def on_input(i, j):
    """click the grid and start input"""
    highlight_related(i, j)
    val = entries[i][j].get()
    val = "".join(sorted(set(c for c in val if c in "123456789")))
    entries[i][j].delete(0, tk.END)
    entries[i][j].insert(0, val)
    
    block_row = i // 3
    block_col = j // 3
    if (block_row + block_col) % 2 == 0:
        bg_color = COLORS["background_white"]
    else:
        bg_color = COLORS["background_gray"]

    if len(val) == 1:
        grid[i][j] = int(val)
        candidates[i][j] = set()
        entries[i][j].config(font=font_big, fg="black", justify="center", bg=bg_color)
    elif len(val) > 1:
        grid[i][j] = None
        candidates[i][j] = set(val)
        entries[i][j].config(font=font_small, fg="gray", justify="left", bg=bg_color)
    else:
        grid[i][j] = None
        candidates[i][j] = set()
        entries[i][j].config(font=font_big, fg="black", justify="center", bg=bg_color)
    
    check_completion()

# check if complete the table
def check_completion():
    global is_paused
    for i in range(9):
        for j in range(9):
            val = entries[i][j].get()
            if not val.isdigit():
                return  
            if int(val) != solution[i][j]:
                return  
    # 如果走到这里说明填满而且正确
    tk.messagebox.showinfo("恭喜！", f"你完成了本题！\n用时：{elapsed_time // 60} 分 {elapsed_time % 60} 秒")

    for i in range(9):
        for j in range(9):
            entry = entries[i][j]
            entry.config(state="disabled")

    is_paused = True

# on click highlight related grids
def clear_highlight():
    """clear highlight in all grids and only keep the background color for 3*3 square"""
    for i in range(9):
        for j in range(9):
            entry = entries[i][j]
            if entry:
                block_row = i // 3
                block_col = j // 3
                if (block_row + block_col) % 2 == 0:
                    bg_color = COLORS["background_white"]   # 白
                else:
                    bg_color = COLORS["background_gray"]  # 灰
                entry.config(bg=bg_color)

def highlight_related(i, j):
    
    clear_highlight()

    # 再把相关格子染浅蓝色
    for row in range(9):
        entries[row][j].config(bg=COLORS["highlight"])  # 同列
    for col in range(9):
        entries[i][col].config(bg=COLORS["highlight"])  # 同行

    # 同宫格
    block_row, block_col = 3 * (i // 3), 3 * (j // 3)
    for r in range(block_row, block_row + 3):
        for c in range(block_col, block_col + 3):
            entries[r][c].config(bg=COLORS["highlight"])
 
# hint function
def show_hint():
    if is_grid_full(grid):
        errors = compare_with_solution(grid, solution)
        if not errors:
            status_label.config(text="🎉 恭喜你完成数独！")
        else:
            for (i, j) in errors:
                entries[i][j].config(bg=COLORS["error"])
            status_label.config(text="❌ 有错误，请检查红色格子")
    else:
        # Step 1: 检查用户填写的确定数字是否正确
        wrong_digits = []
        for i in range(9):
            for j in range(9):
                if puzzle[i][j] is None and grid[i][j] is not None:
                    if grid[i][j] != solution[i][j]:
                        wrong_digits.append((i, j))
                        entries[i][j].config(bg=COLORS["error"])

        if wrong_digits:
            status_label.config(text="❌ 有错误的确定数字，请检查红色格子")
            return  # 不再继续检查候选数
            
        # Step 2: 检查候选数是否合法
        system_candidates = get_candidates(grid)
        invalid = []
        hint_msgs = []
        used_hint_cells = []

        for i in range(9):
            for j in range(9):
                if not candidates[i][j]:
                    continue
                user_cand = set(map(int, candidates[i][j]))
                sys_cand = system_candidates.get((i, j), set())

                if not user_cand.issubset(sys_cand):
                    invalid.append((i, j))
                    entries[i][j].config(bg=COLORS["error"])
                    hint_msgs.append(f"格子({i+1},{j+1}) 的候选数应为: {sorted(sys_cand)}")
                else:
                    used_hint_cells.append((i, j))

        if invalid:
            status_label.config(text="⚠️ 有不合法候选数！\n" + "\n".join(hint_msgs))
            return
            
        # Step 3: 过滤掉用户已使用的提示格子
        all_hints = get_all_hints(grid)
        filtered_hints = [
            hint for hint in all_hints
            if not any(pos in used_hint_cells for pos in hint.get("eliminate_from", []) + hint.get("optimize", []))
        ]

        # 提示优先级1：先检查是否可以使用naked siggle和hidden single方法（最简单的方法）
        priority_0 = [
            h for h in filtered_hints
            if h["technique"] in ["Naked Single", "Hidden Single"]
        ]

        if priority_0:
            best = priority_0[0]
            i, j = best.get("position", (-1, -1))
            status_label.config(
                text=f"✅ {best['technique']}: {best['reason']}"
            )
            if 0 <= i < 9 and 0 <= j < 9:
                entries[i][j].config(bg=COLORS["hint"])
            return

        # 提示优先级2：先对用户填了候选数的格子进行提示   
        priority_1 = [
            hint for hint in filtered_hints
            if any(pos in used_hint_cells for pos in hint.get("eliminate_from", []) + hint.get("optimize", []))
        ]
            
        priority_2 = [
            hint for hint in filtered_hints
            if all(pos not in used_hint_cells for pos in hint.get("eliminate_from", []) + hint.get("optimize", []))
        ]

        ordered_hints = priority_1 + priority_2

        if ordered_hints:
            best_hint = ordered_hints[0]
            status_label.config(
                text=f"🔍 技巧: {best_hint['technique']}\n📌 原因: {best_hint['reason']}"
            )
            for (i, j) in best_hint.get("eliminate_from", []) + best_hint.get("optimize", []):
                entries[i][j].config(bg=COLORS["hint"])
        else:
            status_label.config(text="🟦 当前没有可用的逻辑提示")

# update the grid according to the puzzle
def update_grid(puzzle):
    """This function is used to clear the board for reset/regenerate/load progress,it clears all user input and highlight cauesd by click"""
    for i in range(9):
        for j in range(9):
            entry = entries[i][j]
            entry.config(state="normal")
            entry.delete(0, tk.END)

            block_row = i // 3
            block_col = j // 3
            if (block_row + block_col) % 2 == 0:
                bg_color = COLORS["background_white"]
            else:
                bg_color = COLORS["background_gray"]

            if puzzle[i][j] is not None:
                entry.insert(0, str(puzzle[i][j]))
                entry.config(state="disabled", disabledforeground="black", disabledbackground=bg_color, fg="black", bg=bg_color)
            else:
                entry.config(state="normal", fg="black", bg=bg_color)

# reset function
def reset_board():
    global grid, candidates,is_paused

    for i in range(9):
        for j in range(9):
            entry = entries[i][j]
            if entry is None:
                continue  # 跳过这个格子，防止报错
            
            # 重新判断宫格颜色
            block_row = i // 3
            block_col = j // 3
            if (block_row + block_col) % 2 == 0:
                bg_color = COLORS["background_white"]
            else:
                bg_color = COLORS["background_gray"]

            if puzzle[i][j] is not None:
                grid[i][j] = puzzle[i][j]
                candidates[i][j] = set()
                entry.config(state="normal")
                entries[i][j].delete(0, tk.END)
                entries[i][j].insert(0, str(puzzle[i][j]))
                entries[i][j].config(state="disabled",disabledforeground="black", disabledbackground=bg_color, font=font_big, fg="black", justify="center", bg=bg_color)
            else:
                grid[i][j] = None
                candidates[i][j] = set()
                entries[i][j].config(state="normal")
                entries[i][j].delete(0, tk.END)
                entries[i][j].config(font=font_big, fg="black", justify="center", bg=bg_color)
    
    status_label.config(text="")  # 清空提示栏
    frame.update_idletasks()

# regenerate function
def generate_new_puzzle():
    status_label.config(text="Generating new puzzle...Please wait")
    root.after(100, really_generate_puzzle)  # 100毫秒后真正生成

def really_generate_puzzle():
    global puzzle, solution, grid, candidates, elapsed_time, is_paused

    puzzle, solution, _ = generate_puzzle_by_level(difficulty_var.get())
    grid = [[puzzle[i][j] for j in range(9)] for i in range(9)]
    candidates = [[set() for _ in range(9)] for _ in range(9)]

    update_grid(puzzle)
    # reset the timer
    elapsed_time = 0
    update_timer_display()
    if is_paused:
        is_paused = False
        start_timer()  # 重新启动计时

    status_label.config(text="Generating completed. Good luck!")

# save and load function
def save_progress(filename="sudoku_save.json"):
    global puzzle, grid, candidates, difficulty_var
    data = {
        "puzzle": puzzle,
        "grid": grid,
        "candidates": [[list(cand) for cand in row] for row in candidates],
        "difficulty": difficulty_var.get(),
        "elapsed_time": elapsed_time
    }
    with open(filename, "w") as f:
        json.dump(data, f)
    messagebox.showinfo("保存成功", "✅ 当前进度已成功保存！")

def load_progress(filename="sudoku_save.json"):
    global puzzle, grid, candidates
    
    try:
        with open(filename, "r") as f:
            data = json.load(f)
            puzzle = data["puzzle"]
            grid = data["grid"]
            candidates = [[set(cand) for cand in row] for row in data["candidates"]]
            difficulty_var.set(data["difficulty"])
            elapsed_time = data.get("elapsed_time", 0)
            minutes = elapsed_time // 60
            seconds = elapsed_time % 60
            timer_label.config(text=f"Time: {minutes:02d}:{seconds:02d}")
            update_grid(puzzle)  # 恢复界面
        
        # 确保 entries 都已经创建完毕后再更新界面
        if all(entries[i][j] for i in range(9) for j in range(9)):
            update_grid(puzzle)
        else:
            messagebox.showerror("错误", "❗ 当前界面未初始化，无法加载存档！")

        messagebox.showinfo("读取成功", "✅ 成功读取存档！")

    except FileNotFoundError:
        messagebox.showwarning("存档不存在", "⚠️ 没有找到存档文件，请先保存！")

# timer setup and pause scheme
def start_timer():
    if not is_paused:
        global elapsed_time
        elapsed_time += 1
        update_timer_display()
    root.after(1000, start_timer)

def update_timer_display():
    minutes = elapsed_time // 60
    seconds = elapsed_time % 60
    timer_label.config(text=f"Time: {minutes:02d}:{seconds:02d}")

def toggle_pause():
    global is_paused

    if not is_paused:
        # 进入暂停
        is_paused = True
        overlay_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        overlay_frame.lift()
    else:
        # 恢复继续
        is_paused = False
        overlay_frame.place_forget()

# the main window
def launch_ui():
    global root, entries, frame, difficulty_var, status_label, grid, candidates, timer_label, overlay_frame
    root = tk.Tk()
    root.title("数独解题")
    
    difficulty_var = tk.StringVar(value="Medium")   # default difficulty level=Medium
    # generate new puzzle of corresponding difficulty
    puzzle, solution, difficulty = generate_puzzle_by_level(difficulty_var.get())

    # update input grid and candidates 
    grid = [[puzzle[i][j] for j in range(9)] for i in range(9)]
    candidates = [[set() for _ in range(9)] for _ in range(9)]
    
    # set up timer and pause button frame
    timer_frame = tk.Frame(root)
    timer_frame.grid(row=0, column=0, pady=(5,5))
    
    timer_label = tk.Label(timer_frame, text="Time: 00:00", font=("微软雅黑", 10))
    timer_label.pack(side="left", padx=10)

    pause_button = tk.Button(timer_frame, text="⏸ Pause / Continue", command=toggle_pause)
    pause_button.pack(side="left", padx=10)

    # initialize entry and grid frame
    entries = [[None for _ in range(9)] for _ in range(9)]
    frame = tk.Frame(root)
    frame.grid(row=1, column=0, padx=10, pady=10)
    
    # create grids by loop
    for i in range(9):
        for j in range(9):
            frame.grid_rowconfigure(i, minsize=48)
            frame.grid_columnconfigure(j, minsize=48)
            
            block_row = i // 3
            block_col = j // 3
            if (block_row + block_col) % 2 == 0:
                bg_color = COLORS["background_white"]  
            else:
                bg_color = COLORS["background_gray"]  

            entry = tk.Entry(frame, font=font_big, width=2, justify='center', bd=1, relief='solid', fg="black", bg=bg_color)
            entry.grid(row=i, column=j, sticky="nsew")
            entry.bind("<KeyRelease>", lambda e, i=i, j=j: on_input(i, j))
            entry.bind("<Button-1>", lambda e, i=i, j=j: highlight_related(i, j))
            entries[i][j] = entry
    
    # create a overlay frame for pause
    overlay_frame = tk.Frame(frame, bg="lightgray")
    pause_text = tk.Label(overlay_frame, text="Paused", font=("微软雅黑", 24, "bold"), bg="lightgray")
    pause_text.place(relx=0.5, rely=0.5, anchor="center")
    overlay_frame.place_forget()  # 默认隐藏

    # save&load frame
    save_load_frame = tk.Frame(root)
    save_load_frame.grid(row=2, column=0, pady=(5, 5))

    save_button = tk.Button(save_load_frame, text="💾 保存进度", command=save_progress, width=12)
    save_button.grid(row=0, column=0, padx=5)

    load_button = tk.Button(save_load_frame, text="📂 读取存档", command=load_progress, width=12)
    load_button.grid(row=0, column=1, padx=5)
    
    # button frame
    button_frame = tk.Frame(root)
    button_frame.grid(row=3, column=0, pady=10)
    
    tk.Button(button_frame, text="💡 提示", command=show_hint, width=10).grid(row=0, column=0, pady=5)
    tk.Button(button_frame, text="🔄 重置", command=reset_board, width=10).grid(row=0, column=1, pady=5)
    tk.Button(button_frame, text="🆕 生成新题目", command=generate_new_puzzle, width=12).grid(row=0, column=2, pady=5)
    # difficulty level choose
    tk.OptionMenu(button_frame, difficulty_var, "Easy", "Medium", "Hard", "Extreme").grid(row=0, column=3, pady=5)
    
    # status label
    status_label = tk.Label(root, text="", font=("微软雅黑", 8), fg="blue", justify="left", anchor="w", wraplength=600)
    status_label.grid(row=4, column=0, pady=(5,10))
    
    start_timer()

    root.mainloop()