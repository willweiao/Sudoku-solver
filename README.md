# Sudoku Champion - Intelligent Sudoku Solver App

A complete Sudoku application with an interactive GUI, logical reasoning hints, puzzle generator, and full solution validation.

---

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Logical Techniques Implemented](#logical-techniques-implemented)
- [Project Structure](#project-structure)
- [Build and Release](#build-and-release)
- [Future Improvements](#future-improvements)
- [License](#license)
- [Acknowledgements](#acknowledgements)

---

## Introduction

Sudoku Champion is a Python-based Sudoku solver and game application built with Tkinter.  
It features an interactive graphical user interface (GUI) where users can play Sudoku puzzles of varying difficulties, request real-time logical hints, and validate their solutions.

The project aims to simulate human logical solving strategies and provide an educational as well as an enjoyable Sudoku experience.

---

## Features

- **Interactive GUI** built using Tkinter
- **Sudoku Puzzle Generator** with four difficulty levels: Easy, Medium, Hard, Extreme
- **Real-time Hint System** based on human-like logical reasoning techniques
- **Error Checking** for player inputs with visual highlighting
- **Save and Load Game Progress** locally
- **Timer Functionality** to track solving time
- **Logical Solving Engine** separate from brute-force solving
- **Difficulty Evaluation** based on solving logic complexity
- **Packaged Executable (.exe)** available in Releases for easy download and play

---

## Installation

Requirements:

- Python 3.8 or higher
- Libraries:
  - `numpy`
  - `pandas`
  - `pulp`
  - `tkinter` (comes with Python)

Install dependencies:

```bash
pip install -r requirements.txt

```

Clone the repository:

```bash
git clone https://github.com/your-username/SudokuChampion.git
cd SudokuChampion
```

Run the application:

- Download the application
- Or

```bash
python sudoku_solver_app/main.py
```

---

## Usage

- Start the application.

- Select a difficulty level and generate a new puzzle.

- Fill in the grid by clicking on empty cells.

- Use the Hint button to receive logical solving suggestions.

- Save your current progress or load a previously saved puzzle.

- Pause and resume your gameplay at any time.

---

## Logical Techniques Implemented

The real-time hint system is based on the following solving techniques:

- Naked Single

- Hidden Single

- Naked Subsets (Pairs, Triples, Quads)

- Hidden Subsets

- Pointing

- Claiming

- X-Wing

- Swordfish 

- XY-Wing 

For more details, see the sudoku_tutorial/ folder for full logical techniques documentation.

---

## Project Structure

```bash
sudoku_solver_app/
    ├── assets/                # Static resources (icons, etc.)
    ├── core/                   # Core logic modules (solver, generator, hints)
    ├── ui/                     # Tkinter GUI code
    ├── utils/                  # Helper utilities
    ├── main.py                 # App entry point
sudoku_tutorial/
    └── logical_hints.py         # Tutorial and documentation for solving methods
requirements.txt
README.md
.gitignore
```

---

## Build and Release

The packaged executable "(`.exe`)"can be found in the Releases section.

To build the `.exe` manually:

```bash
python -m PyInstaller --onefile --noconsole --icon=sudoku_solver_app/assets/icon.ico --name=SudokuChampion --add-data "sudoku_solver_app/assets;assets" sudoku_solver_app/main.py
```

After building, the `.exe` will appear in the `/dist/` folder.

---

## Future Improvements

- Implement advanced solving techniques (e.g., Chains, Unique Rectangles)

- Improve GUI design with modern themes

- Add Sudoku puzzle import/export

- Add a web-based or mobile app version

- Develop a difficulty rating system based on actual solving steps

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgements

- PuLP library for ILP optimization

- Community resources on human Sudoku solving strategies: 
    - [sudoku.com/skills](https://sudoku.com/sudoku-rules/)
    - [favourite sudoku content creator](https://space.bilibili.com/99132936)
    - [sudoku.com youtube profile](https://www.youtube.com/@sudoku.easybrain)



