import tkinter as tk

root = tk.Tk()
root.title("数独")

font_big = ("Helvetica", 18)
font_small = ("Arial", 7)

sudoku_puzzle = [
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

entries = [[None for _ in range(9)] for _ in range(9)]
grid = [[sudoku_puzzle[i][j] for j in range(9)] for i in range(9)]
candidates = [[set() for _ in range(9)] for _ in range(9)]

def on_input(i, j):
    val = entries[i][j].get()
    filtered = "".join(sorted(set(c for c in val if c in "123456789")))
    entries[i][j].delete(0, tk.END)
    entries[i][j].insert(0, filtered)

    if len(filtered) == 1:
        grid[i][j] = int(filtered)
        candidates[i][j] = set()
        entries[i][j].config(font=font_big, fg="black", justify='center')
    elif len(filtered) > 1:
        grid[i][j] = None
        candidates[i][j] = set(filtered)
        entries[i][j].config(font=font_small, fg="gray", justify='left')
    else:
        grid[i][j] = None
        candidates[i][j] = set()
        entries[i][j].config(font=font_big, fg="black", justify='center')

grid_frame = tk.Frame(root)
grid_frame.grid(row=0, column=0, padx=10, pady=10)

for i in range(9):
    for j in range(9):
        grid_frame.grid_rowconfigure(i, minsize=48)
        grid_frame.grid_columnconfigure(j, minsize=48)

        val = sudoku_puzzle[i][j]
        if val is not None:
            label = tk.Label(grid_frame, text=str(val), font=font_big, width=2, height=1,
                             fg="black", bg="#f0f0f0", relief="solid", bd=1)
            label.grid(row=i, column=j, sticky="nsew")
        else:
            entry = tk.Entry(grid_frame, font=font_big, width=2, justify='center')
            entry.grid(row=i, column=j, sticky="nsew")
            entry.bind("<KeyRelease>", lambda e, i=i, j=j: on_input(i, j))
            entries[i][j] = entry

root.mainloop()