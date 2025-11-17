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
