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