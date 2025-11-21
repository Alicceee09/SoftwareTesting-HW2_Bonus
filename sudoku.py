import copy
import random

class SudokuBoard:
    def __init__(self, grid):
        # Deep copy so solving/generation does not mutate caller data
        self.grid = copy.deepcopy(grid)
        self.size = 9

    def is_valid(self, row, col, num):
        for i in range(self.size):
            if self.grid[row][i] == num:
                return False

        for i in range(self.size):
            if self.grid[i][col] == num:
                return False

        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                if self.grid[start_row + i][start_col + j] == num:
                    return False

        return True

    def find_empty(self):
        for i in range(self.size):
            for j in range(self.size):
                if self.grid[i][j] == 0:
                    return (i, j)
        return None

    def solve(self, randomize=False):
        find = self.find_empty()
        if not find:
            return True

        row, col = find
        numbers = list(range(1, self.size + 1))
        if randomize:
            random.shuffle(numbers)

        for num in numbers:
            if self.is_valid(row, col, num):
                self.grid[row][col] = num
                if self.solve(randomize):
                    return True
                self.grid[row][col] = 0

        return False

    # 2-1 Uniqueness Guarantee in Generator
    def count_solutions(self, limit=2):
        count = 0

        def backtrack():
            nonlocal count

            if count >= limit:
                return

            find = self.find_empty()
            if not find:
                count += 1
                return

            row, col = find
            for num in range(1, self.size + 1):
                if self.is_valid(row, col, num):
                    self.grid[row][col] = num
                    backtrack()
                    self.grid[row][col] = 0

                    if count >= limit:
                        return

        backtrack()
        return count


def generate(difficulty):
    empty_grid = [[0] * 9 for _ in range(9)]
    solution_seed = SudokuBoard(empty_grid)
    solution_seed.solve(randomize=True)
    solution_grid = copy.deepcopy(solution_seed.grid)

    puzzle_board = SudokuBoard(solution_grid)
    cells_to_remove = difficulty

    attempts = 0
    max_attempts = difficulty * 10  # avoid infinite loop

    while cells_to_remove > 0 and attempts < max_attempts:
        attempts += 1

        row = random.randint(0, 8)
        col = random.randint(0, 8)

        if puzzle_board.grid[row][col] == 0:
            continue

        removed_value = puzzle_board.grid[row][col]
        puzzle_board.grid[row][col] = 0

        attempt_board = SudokuBoard(puzzle_board.grid)
        num_solutions = attempt_board.count_solutions(limit=2)

        if num_solutions == 1:
            cells_to_remove -= 1
        else:
            puzzle_board.grid[row][col] = removed_value

    solution_board = SudokuBoard(solution_grid)
    return puzzle_board, solution_board


# 2.2: Difficulty Rating Engine

def rate_difficulty(grid):
    """
    Return a rough human-style difficulty rating based on the hardest technique required.
    Easy: solved by Naked/Hidden Singles
    Medium: requires Naked/Hidden Pairs or Pointing Pairs (plus singles)
    Hard: requires techniques beyond the above (falls back to full solver)
    """
    
    def build_candidates(state_grid):
        candidates = [[set() for _ in range(9)] for _ in range(9)]
        temp_board = SudokuBoard(state_grid)
        for r in range(9):
            for c in range(9):
                if state_grid[r][c] != 0:
                    continue
                for num in range(1, 10):
                    if temp_board.is_valid(r, c, num):
                        candidates[r][c].add(num)
        return candidates

    def units_for_cell(r, c):
        rows = [(r, cc) for cc in range(9)]
        cols = [(rr, c) for rr in range(9)]
        sr, sc = 3 * (r // 3), 3 * (c // 3)
        box = [(sr + dr, sc + dc) for dr in range(3) for dc in range(3)]
        return rows, cols, box

    working_grid = copy.deepcopy(grid)
    givens = sum(1 for row in working_grid for val in row if val != 0)
    techniques_used = set()

    def apply_strategies(allow_pairs):
        nonlocal working_grid
        candidates = build_candidates(working_grid)

        while True:
            progress = False

            # Naked Singles
            for r in range(9):
                for c in range(9):
                    if working_grid[r][c] == 0 and len(candidates[r][c]) == 1:
                        val = next(iter(candidates[r][c]))
                        working_grid[r][c] = val
                        techniques_used.add("naked_single")
                        candidates = build_candidates(working_grid)
                        progress = True
            if progress:
                continue

            # Hidden Singles
            for unit in range(9):
                # Rows
                counts = {}
                for c in range(9):
                    for val in candidates[unit][c]:
                        counts.setdefault(val, []).append((unit, c))
                for val, cells in counts.items():
                    if len(cells) == 1:
                        r, c = cells[0]
                        working_grid[r][c] = val
                        techniques_used.add("hidden_single")
                        candidates = build_candidates(working_grid)
                        progress = True
                if progress:
                    break

                # Columns
                counts = {}
                for r in range(9):
                    for val in candidates[r][unit]:
                        counts.setdefault(val, []).append((r, unit))
                for val, cells in counts.items():
                    if len(cells) == 1:
                        r, c = cells[0]
                        working_grid[r][c] = val
                        techniques_used.add("hidden_single")
                        candidates = build_candidates(working_grid)
                        progress = True
                if progress:
                    break

                # Boxes
                counts = {}
                br, bc = 3 * (unit // 3), 3 * (unit % 3)
                box_cells = [(br + dr, bc + dc) for dr in range(3) for dc in range(3)]
                for (r, c) in box_cells:
                    for val in candidates[r][c]:
                        counts.setdefault(val, []).append((r, c))
                for val, cells in counts.items():
                    if len(cells) == 1:
                        r, c = cells[0]
                        working_grid[r][c] = val
                        techniques_used.add("hidden_single")
                        candidates = build_candidates(working_grid)
                        progress = True
                if progress:
                    break
            if progress:
                continue

            if not allow_pairs:
                break

            # Naked Pairs
            def apply_naked_pairs(get_unit_cells):
                nonlocal candidates
                changed = False
                for idx in range(9):
                    cells = get_unit_cells(idx)
                    pairs = {}
                    for r, c in cells:
                        if working_grid[r][c] != 0:
                            continue
                        if len(candidates[r][c]) == 2:
                            key = tuple(sorted(candidates[r][c]))
                            pairs.setdefault(key, []).append((r, c))
                    for pair_vals, pair_cells in pairs.items():
                        if len(pair_cells) == 2:
                            for r, c in cells:
                                if working_grid[r][c] != 0 or (r, c) in pair_cells:
                                    continue
                                before = len(candidates[r][c])
                                candidates[r][c] -= set(pair_vals)
                                if len(candidates[r][c]) != before:
                                    changed = True
                    if changed:
                        techniques_used.add("naked_pair")
                return changed

            def row_cells(r):
                return [(r, c) for c in range(9)]

            def col_cells(c):
                return [(r, c) for r in range(9)]

            def box_cells(idx):
                br, bc = 3 * (idx // 3), 3 * (idx % 3)
                return [(br + dr, bc + dc) for dr in range(3) for dc in range(3)]

            if apply_naked_pairs(row_cells) or apply_naked_pairs(col_cells) or apply_naked_pairs(box_cells):
                progress = True

            # Pointing Pairs / Triples
            if not progress:
                for box_idx in range(9):
                    br, bc = 3 * (box_idx // 3), 3 * (box_idx % 3)
                    box = [(br + dr, bc + dc) for dr in range(3) for dc in range(3)]
                    for val in range(1, 10):
                        locations = [(r, c) for (r, c) in box if working_grid[r][c] == 0 and val in candidates[r][c]]
                        if not locations:
                            continue
                        rows = {r for r, _ in locations}
                        cols = {c for _, c in locations}
                        if len(rows) == 1:
                            target_row = next(iter(rows))
                            for c in range(9):
                                if (target_row, c) not in box and working_grid[target_row][c] == 0:
                                    before = len(candidates[target_row][c])
                                    candidates[target_row][c].discard(val)
                                    if len(candidates[target_row][c]) != before:
                                        progress = True
                                        techniques_used.add("pointing_pair")
                        if len(cols) == 1:
                            target_col = next(iter(cols))
                            for r in range(9):
                                if (r, target_col) not in box and working_grid[r][target_col] == 0:
                                    before = len(candidates[r][target_col])
                                    candidates[r][target_col].discard(val)
                                    if len(candidates[r][target_col]) != before:
                                        progress = True
                                        techniques_used.add("pointing_pair")

            if not progress:
                break

        return working_grid

    # Stage 1: singles only
    apply_strategies(allow_pairs=False)
    if SudokuBoard(working_grid).find_empty() is None:
        return "Easy"

    # Stage 2: singles + pairs/pointing
    apply_strategies(allow_pairs=True)
    if SudokuBoard(working_grid).find_empty() is None:
        if "naked_pair" in techniques_used or "pointing_pair" in techniques_used:
            return "Medium"
        return "Easy"

    # Stage 3: fallback to full solver, otherwise treat as Hard/Unsolvable
    fallback = SudokuBoard(working_grid)
    if fallback.solve():
        # Use clue count as a simple proxy: harder when clues are sparse
        if givens <= 25:
            return "Hard"
        return "Medium"
    return "Unsolvable"
