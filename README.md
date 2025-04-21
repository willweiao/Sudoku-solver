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