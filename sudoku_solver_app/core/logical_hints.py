import numpy as np
import pandas as pd
from itertools import combinations
from collections import defaultdict


def get_all_hints(table):
    candidates_dict = get_candidates(table)
    all_hints = []

    # get hints by row/col/square from each available ethods
    for axis in ["r", "c", "s"]:
        for i in range(9):
            if axis == "r":
                pos = (i, 0)
            elif axis == "c":
                pos = (0, i)
            else:
                pos = (3 * (i // 3), 3 * (i % 3))
            sub_candidates = select_candidates(pos, candidates_dict, axis)

            all_hints += hidden_subset_elimination_hint(sub_candidates)
            all_hints += naked_subset_elimination_hint(sub_candidates)

            if axis == "s":
                all_hints += pointing_elimination_hint(pos, candidates_dict)

    # method that apply not on axis(s)
    all_hints += claiming_elimination_hint(candidates_dict)
    all_hints += xwing_hint(candidates_dict)

    return all_hints


def if_valid(table, row, col, num):
    # check if number if valid within the row and column
    for i in range(9):
      if table[row][i]==num or table[i][col]==num:
         return False
    # check if valid in the 3*3 square
    start_row, start_col = 3 * (row // 3), 3 * (col// 3)
    for i in range(3):
        for j in range(3):
            if table[start_row + i][start_col + j] == num:
                return False
    return True


# Find possible digits for each position
def get_candidates(table):
    candidates_dict={}
    for row in range(9):
        for col in range(9):
            if table[row][col] is None:
                candidates = set()
                for num in range(1,10):
                    if if_valid(table,row,col,num):
                        candidates.add(num)
                candidates_dict[(row,col)]=candidates
    
    return candidates_dict


# take out the row/col/square candidate dictionary in one function
def select_candidates(pos, candidates_dict, axis):
    """
    attribute "axis" denotes which candidates dict in this iteration we are focusing on
            axis == "r" : take out the row candidates
            axis == "c" : take out the column candidates
            axis == "s" : take out the square candidates
    """
    row,col=pos
    selected_candidates={}

    if axis == "r":
        selected_candidates = {k: v for k, v in candidates_dict.items() if k[0] == row}

    elif axis == "c":
        selected_candidates = {k: v for k, v in candidates_dict.items() if k[1] == col}

    elif axis == "s":
        start_row = 3 * (row // 3)
        start_col = 3 * (col // 3)
        selected_candidates = {
            k: v for k, v in candidates_dict.items()
            if start_row <= k[0] < start_row + 3 and start_col <= k[1] < start_col + 3
        }

    return selected_candidates


# hint by naked subset elimination
def naked_subset_elimination_hint(candidates_dict):
    
    hints=[]
    keys = list(candidates_dict.keys()) 
    N = len(candidates_dict)
    
    for n in range(1, N):
        for combo in combinations(keys, n):
            union_set = set()
            for key in combo:
                union_set.update(candidates_dict[key])
            
            
            if len(union_set) == n:
                rest = [k for k in keys if k not in combo]
                affected = []
                for rest_key in rest:
                    if union_set & candidates_dict[rest_key]:  # candidates dict can be optimized
                        affected.append(rest_key)
            
                if affected:
                        hints.append({
                            "technique": f"Naked Subset ({n})",
                            "subset_cells": list(combo),
                            "naked_values": list(union_set),
                            "eliminate_from": affected,
                            "reason": f"Cells {combo} contain only {union_set}, remove from others"
                        })

    return hints


# hint by hidden subset elimination
def hidden_subset_elimination_hint(candidates_dict):
    hints=[]
    
    num_positions = defaultdict(list)   
    # decide which position a num appears
    for pos, candidates in candidates_dict.items():
        for num in candidates:
            num_positions[num].append(pos)

    # to check if there are hidden single/pair/triple/quad
    for n in range(1,5):
        for nums in combinations(num_positions.keys(), n):
            positions = set()

            for num in nums:
                positions.update(num_positions[num])
            
            
            if len(positions) == n:
                affected_positions = []
                for pos in positions:
                    current = candidates_dict[pos]
               
                    if current != set(nums):  
                        affected_positions.append(pos)

                if affected_positions:
                    hints.append({
                        "technique": f"Hidden Subset ({n})",
                        "numbers": list(nums),
                        "positions": list(positions),
                        "optimize": affected_positions,
                        "reason": f"Only numbers {nums} appear in {positions}, keep only those"
                    })

    
    return hints


# hint by pointing elimination
def pointing_elimination_hint(pos, candidates_dict):
    square_candidates = select_candidates(pos, candidates_dict, axis="s")
    hints=[]

    for num in range(1, 10):
        positions_with_num = [p for p, v in square_candidates.items() if num in v]
        
        if len(positions_with_num) <= 1:
            continue

        rows = {r for r, _ in positions_with_num}
        cols = {c for _, c in positions_with_num}

        if len(rows) == 1:
            target_row = next(iter(rows))
            eliminate_positions=[]
            for col in range(9):
                if (target_row, col) not in square_candidates and (target_row, col) in candidates_dict:
                    if num in candidates_dict[(target_row,col)]:
                        eliminate_positions.append((target_row,col))
            
            if eliminate_positions:
                hints.append({
                    "technique": "Pointing",
                    "number": num,
                    "square": (pos[0] // 3, pos[1] // 3),
                    "direction": "row",
                    "line": target_row,
                    "eliminate_from": eliminate_positions,
                    "reason": f"In square ({pos[0]//3},{pos[1]//3}), number {num} only appears in row {target_row} → eliminate elsewhere in row"
                })

        elif len(cols) == 1:
            target_col = next(iter(cols))
            eliminate_positions = []
            for row in range(9):
                if (row, target_col) not in square_candidates and (row, target_col) in candidates_dict:
                    if num in candidates_dict[(row, target_col)]:
                        eliminate_positions.append((row, target_col))

            if eliminate_positions:
                hints.append({
                    "technique": "Pointing",
                    "number": num,
                    "square": (pos[0] // 3, pos[1] // 3),
                    "direction": "col",
                    "line": target_col,
                    "eliminate_from": eliminate_positions,
                    "reason": f"In square ({pos[0]//3},{pos[1]//3}), number {num} only appears in col {target_col} → eliminate elsewhere in column"
                })

    return hints


# hints by x wing
def xwing_hint(candidates_dict):
    hints = []

    # scan the rows for xwing structures
    for num in range(1, 10):
        row_to_cols = defaultdict(list)
        for (row, col), cand in candidates_dict.items():
            if num in cand:
                row_to_cols[row].append(col)

        rows = list(row_to_cols.keys())
        for r1, r2 in combinations(rows, 2):
            c1s = row_to_cols[r1]
            c2s = row_to_cols[r2]

            if len(c1s) == 2 and c1s == c2s:
                col1, col2 = c1s
                eliminate = []
                for row in range(9):
                    if row not in {r1, r2}:
                        for col in [col1, col2]:
                            if (row, col) in candidates_dict and num in candidates_dict[(row, col)]:
                                eliminate.append((row, col))
                if eliminate:
                    hints.append({
                        "technique": "X-Wing",
                        "orientation": "row",
                        "number": num,
                        "lines": [r1, r2],
                        "shared_units": [col1, col2],
                        "eliminate_from": eliminate,
                        "reason": f"X-Wing on rows {r1} and {r2}, columns {col1} and {col2} for number {num}"
                    })

    # scan the columns for xwing structures
    for num in range(1, 10):
        col_to_rows = defaultdict(list)
        for (row, col), cand in candidates_dict.items():
            if num in cand:
                col_to_rows[col].append(row)

        cols = list(col_to_rows.keys())
        for c1, c2 in combinations(cols, 2):
            r1s = col_to_rows[c1]
            r2s = col_to_rows[c2]

            if len(r1s) == 2 and r1s == r2s:
                row1, row2 = r1s
                eliminate = []
                for col in range(9):
                    if col not in {c1, c2}:
                        for row in [row1, row2]:
                            if (row, col) in candidates_dict and num in candidates_dict[(row, col)]:
                                eliminate.append((row, col))
                if eliminate:
                    hints.append({
                        "technique": "X-Wing",
                        "orientation": "col",
                        "number": num,
                        "lines": [c1, c2],
                        "shared_units": [row1, row2],
                        "eliminate_from": eliminate,
                        "reason": f"X-Wing on columns {c1} and {c2}, rows {row1} and {row2} for number {num}"
                    })

    return hints


# hints by claiming elimination
def claiming_elimination_hint(candidates_dict):
    hints = []

    for num in range(1, 10):
        for row in range(9):
            positions = [(row, col) for col in range(9)
                         if (row, col) in candidates_dict and num in candidates_dict[(row, col)]]
            if len(positions) < 2:
                continue
            
            blocks = {(r // 3, c // 3) for r, c in positions}
            if len(blocks) == 1:
                block_row, block_col = next(iter(blocks))
                eliminate = []
                for r in range(3 * block_row, 3 * block_row + 3):
                    for c in range(3 * block_col, 3 * block_col + 3):
                        if r != row and (r, c) in candidates_dict and num in candidates_dict[(r, c)]:
                            eliminate.append((r, c))

                if eliminate:
                    hints.append({
                        "technique": "Claiming",
                        "number": num,
                        "line_type": "row",
                        "line": row,
                        "square": (block_row, block_col),
                        "eliminate_from": eliminate,
                        "reason": f"In row {row}, number {num} only appears in square ({block_row},{block_col}), so eliminate it from other cells in that square"
                    })

        for col in range(9):
            positions = [(row, col) for row in range(9)
                         if (row, col) in candidates_dict and num in candidates_dict[(row, col)]]
            if len(positions) < 2:
                continue
            blocks = {(r // 3, c // 3) for r, c in positions}
            if len(blocks) == 1:
                block_row, block_col = next(iter(blocks))
                eliminate = []
                for r in range(3 * block_row, 3 * block_row + 3):
                    for c in range(3 * block_col, 3 * block_col + 3):
                        if c != col and (r, c) in candidates_dict and num in candidates_dict[(r, c)]:
                            eliminate.append((r, c))
                            
                if eliminate:
                    hints.append({
                        "technique": "Claiming",
                        "number": num,
                        "line_type": "col",
                        "line": col,
                        "square": (block_row, block_col),
                        "eliminate_from": eliminate,
                        "reason": f"In column {col}, number {num} only appears in square ({block_row},{block_col}), so eliminate it from other cells in that square"
                    })

    return hints