from generator import generate_puzzle_by_level

def test_generate_puzzles():
    levels = ["Easy", "Medium", "Hard", "Extreme"]
    
    for level in levels:
        print(f"\n=== Generating a {level} Sudoku ===")
        puzzle, solution, difficulty = generate_puzzle_by_level(level)

        clues = sum(1 for row in puzzle for cell in row if cell is not None)
        holes = 81 - clues

        print(f"Generated difficulty: {difficulty}")
        print(f"Number of holes: {holes}")
        print("Puzzle:")
        for row in puzzle:
            print(" ".join(str(cell) if cell is not None else "." for cell in row))

if __name__ == "__main__":
    test_generate_puzzles()