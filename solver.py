# solver.py

import numpy as np


class Solver:
    def __init__(self, board: np.ndarray, groups):
        self.board = board
        self.groups = groups

        self.group_at = {}
        for group in groups:
            for cell in group.cells:
                self.group_at[cell] = group

    def solve(self):
        find = self.find_empty()
        if not find:
            return True
        else:
            row, col = find

        for i in range(1, 10):
            if self.valid(i, (row, col)):
                self.board[row][col] = i

                if self.solve():
                    return True

                self.board[row][col] = 0

        return False

    def valid(self, num, pos):

        # Check group
        group = self.group_at[pos]
        s = 0
        for y, x in group.cells:
            v = self.board[y, x]
            if v == num:
                return False
            s += v
            if s + num > group.sum:
                return False

        # Check row
        for i in range(9):
            if self.board[pos[0], i] == num and pos[1] != i:
                return False

        # Check column
        for i in range(9):
            if self.board[i, pos[1]] == num and pos[0] != i:
                return False

        # Check box
        box_x = pos[1] // 3
        box_y = pos[0] // 3

        for i in range(box_y * 3, box_y * 3 + 3):
            for j in range(box_x * 3, box_x * 3 + 3):
                if self.board[i][j] == num and (i, j) != pos:
                    return False

        return True

    def find_empty(self):
        for group in self.groups:
            for y, x in group.cells:
                if self.board[y, x] == 0:
                    return y, x  # row, col

        return None
