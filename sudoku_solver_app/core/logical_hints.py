import numpy as np
import pandas as pd
from itertools import combinations
from collections import defaultdict

# 用于提示坐标的可读转换
def pos_human(pos):
    return f"({pos[0]+1},{pos[1]+1})"

def positions_human(pos_list):
    return [pos_human(p) for p in pos_list]

def get_all_hints(table):
    candidates_dict = get_candidates(table)
    
    # 1️⃣ 先尝试 Naked Single（只有一个候选）
    naked_hints = naked_single_hint(candidates_dict)
    if naked_hints:
        return naked_hints

    # 2️⃣ 再尝试 Hidden Single（某数字只能出现在一个格子）
    hidden_hints = hidden_single_hint(candidates_dict)
    if hidden_hints:
        return hidden_hints
    
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
            
            if axis == "s":
                all_hints += pointing_elimination_hint(pos, candidates_dict)
            
            sub_candidates = select_candidates(pos, candidates_dict, axis)

            all_hints += hidden_subset_elimination_hint(sub_candidates)
            all_hints += naked_subset_elimination_hint(sub_candidates)

    # method that apply not on axis(s)
    all_hints += claiming_elimination_hint(candidates_dict)
    all_hints += xwing_hint(candidates_dict)
    all_hints += xy_wing_hint(candidates_dict)
    all_hints += swordfish_hint(candidates_dict)

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


# hint by hidden single
def hidden_single_hint(candidates_dict):
    hints = []
    num_pos = defaultdict(list)
    for (r, c), cand in candidates_dict.items():
        for num in cand:
            num_pos[(r, num)].append((r, c))
            num_pos[(c, num, "col")].append((r, c))
            num_pos[((r//3, c//3), num, "box")].append((r, c))

    for key, positions in num_pos.items():
        if len(positions) == 1:
            pos = positions[0]
            hints.append({
                "technique": "Hidden Single",
                "number": key[1],
                "position": pos,
                "reason": f"Number {key[1]} can only appear once in {key[:2]}, must go to {pos[0]+1},{pos[1]+1}"
            })
    return hints


# hint by naked single 
def naked_single_hint(candidates_dict):
    hints = []
    for (row, col), candidates in candidates_dict.items():
        if len(candidates) == 1:
            num = next(iter(candidates))
            hints.append({
                "technique": "Naked Single",
                "number": num,
                "position": (row, col),
                "reason": f"Cell ({row+1},{col+1}) can only have {num}, since others are not allowed"
            })
    return hints


# hint by naked subset elimination
def naked_subset_elimination_hint(candidates_dict):
    hints=[]

    if len(candidates_dict) < 2:
        return []
    
    keys = list(candidates_dict.keys()) 
    N = len(candidates_dict)
    
    for n in range(2, N):
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
                            "reason": f"Cells {positions_human(combo)} contain only {union_set}, remove from others"
                        })

    return hints


# hint by hidden subset elimination
def hidden_subset_elimination_hint(candidates_dict):
    hints=[]

    if len(candidates_dict) < 2:
        return []
    
    num_positions = defaultdict(list)   
    # decide which position a num appears
    for pos, candidates in candidates_dict.items():
        for num in candidates:
            num_positions[num].append(pos)
    
    # to check if there are hidden single/pair/triple/quad
    max_subset_size = min(len(candidates_dict) - 1, 4)
    for n in range(2,max_subset_size+1):
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
                        "reason": f"Only numbers {nums} appear in {positions_human(positions)}, keep only those"
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
                    "square": (pos[0] // 3 +1, pos[1] // 3 +1),
                    "direction": "row",
                    "line": target_row,
                    "eliminate_from": eliminate_positions,
                    "reason": f"In square ({pos[0]//3+1},{pos[1]//3+1}), number {num} only appears in row {target_row+1} → eliminate elsewhere in this row"
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
                    "square": (pos[0] // 3+1, pos[1] // 3+1),
                    "direction": "col",
                    "line": target_col,
                    "eliminate_from": eliminate_positions,
                    "reason": f"In square ({pos[0]//3+1},{pos[1]//3+1}), number {num} only appears in col {target_col+1} → eliminate elsewhere in column"
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
                        "lines": [r1+1, r2+1],
                        "shared_units": [col1+1, col2+1],
                        "eliminate_from": eliminate,
                        "reason": f"X-Wing on rows {r1+1} and {r2+1}, columns {col1+1} and {col2+1} for number {num}"
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
                        "lines": [c1+1, c2+1],
                        "shared_units": [row1+1, row2+1],
                        "eliminate_from": eliminate,
                        "reason": f"X-Wing on columns {c1+1} and {c2+1}, rows {row1+1} and {row2+1} for number {num}"
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
                        "line": row+1,
                        "square": (block_row+1, block_col+1),
                        "eliminate_from": eliminate,
                        "reason": f"In row {row+1}, number {num} only appears in square ({block_row+1},{block_col+1}), so eliminate it from other cells in that square"
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
                        "line": col+1,
                        "square": (block_row+1, block_col+1),
                        "eliminate_from": eliminate,
                        "reason": f"In column {col+1}, number {num} only appears in square ({block_row+1},{block_col+1}), so eliminate it from other cells in that square"
                    })

    return hints


# hint by swordfish
def swordfish_hint(candidates_dict):
    hints = []

    # 行扫描：寻找行上的剑鱼结构（数字出现在相同的三列）
    for num in range(1, 10):
        row_to_cols = defaultdict(list)
        for (row, col), cand in candidates_dict.items():
            if num in cand:
                row_to_cols[row].append(col)

        rows = list(row_to_cols.keys())
        for r1, r2, r3 in combinations(rows, 3):
            c1s = row_to_cols[r1]
            c2s = row_to_cols[r2]
            c3s = row_to_cols[r3]

            common_cols = set(c1s) & set(c2s) & set(c3s)
            if len(common_cols) == 3:
                eliminate = []
                for row in range(9):
                    if row not in {r1, r2, r3}:
                        for col in common_cols:
                            if (row, col) in candidates_dict and num in candidates_dict[(row, col)]:
                                eliminate.append((row, col))
                if eliminate:
                    hints.append({
                        "technique": "Swordfish",
                        "orientation": "row",
                        "number": num,
                        "lines": [r1, r2, r3],
                        "shared_units": list(common_cols),
                        "eliminate_from": eliminate,
                        "reason": f"Swordfish: number {num} in rows {r1+1}, {r2+1}, {r3+1} in same cols {sorted(common_cols)}"
                    })

    # 列扫描：寻找列上的剑鱼结构（数字出现在相同的三行）
    for num in range(1, 10):
        col_to_rows = defaultdict(list)
        for (row, col), cand in candidates_dict.items():
            if num in cand:
                col_to_rows[col].append(row)

        cols = list(col_to_rows.keys())
        for c1, c2, c3 in combinations(cols, 3):
            r1s = col_to_rows[c1]
            r2s = col_to_rows[c2]
            r3s = col_to_rows[c3]

            common_rows = set(r1s) & set(r2s) & set(r3s)
            if len(common_rows) == 3:
                eliminate = []
                for col in range(9):
                    if col not in {c1, c2, c3}:
                        for row in common_rows:
                            if (row, col) in candidates_dict and num in candidates_dict[(row, col)]:
                                eliminate.append((row, col))
                if eliminate:
                    hints.append({
                        "technique": "Swordfish",
                        "orientation": "col",
                        "number": num,
                        "lines": [c1, c2, c3],
                        "shared_units": list(common_rows),
                        "eliminate_from": eliminate,
                        "reason": f"Swordfish: number {num} in cols {c1+1}, {c2+1}, {c3+1} in same rows {sorted(common_rows)}"
                    })

    return hints


# hint by xy_wing
def xy_wing_hint(candidates_dict):
    hints = []

    # 寻找所有有两个候选数的格子作为 XY-Wing 的主格
    two_candidate_cells = [pos for pos, cand in candidates_dict.items() if len(cand) == 2]

    for pivot in two_candidate_cells:
        pivot_cand = candidates_dict[pivot]
        x, y = pivot_cand

        # 找到两个与 pivot 共享一个候选数的单元格，作为 wings
        wing_cells = []
        for wing in candidates_dict:
            if wing == pivot or len(candidates_dict[wing]) != 2:
                continue
            if is_peer(pivot, wing):  # 需要同一行、列或宫格
                wing_cand = candidates_dict[wing]
                if x in wing_cand or y in wing_cand:
                    wing_cells.append(wing)

        # 组合两个 wing 试探 XY-Wing 构型
        for w1, w2 in combinations(wing_cells, 2):
            if w1 == w2 or not is_peer(w1, w2):
                continue
            w1_cand = candidates_dict[w1]
            w2_cand = candidates_dict[w2]
            all_cand = {x, y}

            if (pivot_cand == w1_cand or pivot_cand == w2_cand):
                continue  # wing 候选和 pivot 完全一样，不构成 xy-wing

            union1 = pivot_cand.union(w1_cand)
            union2 = pivot_cand.union(w2_cand)
            intersection = w1_cand & w2_cand
            z = list(intersection - pivot_cand)

            if len(z) != 1:
                continue

            z = z[0]

            # 确定可以被排除 z 的位置（pivot, w1, w2 三者公共影响区）
            common_peers = get_common_peers([pivot, w1, w2])
            eliminate = []
            for peer in common_peers:
                if peer in candidates_dict and z in candidates_dict[peer]:
                    eliminate.append(peer)
            # 🚫 过滤掉自身
            eliminate = [pos for pos in eliminate if pos not in {pivot, w1, w2}]

            if eliminate:
                hints.append({
                    "technique": "XY-Wing",
                    "pivot": pivot,
                    "wings": [w1, w2],
                    "eliminate_z": z,
                    "eliminate_from": eliminate,
                    "reason": f"XY-Wing formed with pivot {pivot} and wings {w1}, {w2} eliminates {z} from {eliminate}"
                })

    return hints

# 判断两个格子是否是同行、同列或同宫格（可以影响）
def is_peer(a, b):
    return (
        a[0] == b[0] or  # 同行
        a[1] == b[1] or  # 同列
        (a[0] // 3 == b[0] // 3 and a[1] // 3 == b[1] // 3)  # 同宫格
    )

# 返回多个格子共有的影响区域（同行/列/宫格交集）
def get_common_peers(positions):
    peer_sets = []
    for pos in positions:
        r, c = pos
        peers = set()

        for i in range(9):
            peers.add((r, i))
            peers.add((i, c))

        start_r, start_c = 3 * (r // 3), 3 * (c // 3)
        for i in range(start_r, start_r + 3):
            for j in range(start_c, start_c + 3):
                peers.add((i, j))

        peer_sets.append(peers)

    return set.intersection(*peer_sets)