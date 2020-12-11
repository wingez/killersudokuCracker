import pulp

import numpy as np

from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class Cage:
    sum: int
    cells: List[Tuple[int, int]]


class KillerSudoku:
    def __init__(self):
        self.grid = np.zeros((9, 9))
        self.cages: List[Cage] = []

    def add_cage(self, total: int, cells: List[Tuple[int, int]]):
        self.cages.append(Cage(sum=total, cells=cells))

    def print(self):
        print(self.grid)

    def solve(self):
        solver = KillerSudokuSolver(self)
        solver.solve()


class KillerSudokuSolver:
    rows = list(range(9))
    columns = list(range(9))
    values = list(range(1, 10))

    def __init__(self, sudoku: KillerSudoku):
        self._sudoku = sudoku

        self.problem = pulp.LpProblem("Killer_sudoku_problem")
        self.choices = pulp.LpVariable.dicts(
            "Choice", (self.values, self.rows, self.columns), cat=pulp.const.LpBinary
        )

    def _apply_sudoku_constraints(self):
        # One digit per cell
        for row in self.rows:
            for column in self.columns:
                self.problem += pulp.lpSum([self.choices[v][row][column] for v in self.values]) == 1

        # Each digit one time per row/column/box
        for value in self.values:
            for row in self.rows:
                self.problem += pulp.lpSum([self.choices[value][row][column] for column in self.columns]) == 1

            for column in self.columns:
                self.problem += pulp.lpSum([self.choices[value][row][column] for row in self.rows]) == 1

            boxes = [
                [(row, column) for row in range(i, i + 3) for column in range(j, j + 3)]
                for i in range(0, 9, 3) for j in range(0, 9, 3)
            ]

            for box in boxes:
                self.problem += pulp.lpSum([self.choices[value][row][column] for row, column in box]) == 1

    def _apply_cage_constraints(self):
        for cage in self._sudoku.cages:
            constraints = [
                self.choices[val][row][column] * val for row, column in cage.cells for val in self.values
            ]
            self.problem += pulp.lpSum(constraints) == cage.sum

            for value in self.values:
                self.problem += pulp.lpSum([self.choices[value][row][column] for row, column in cage.cells]) <= 1

            # TODO apply each digit at most once per cell

    def solve(self):
        self._apply_sudoku_constraints()
        self._apply_cage_constraints()

        self.problem.solve()
        if not self.problem.status == 1:
            raise AssertionError('Sudoku could not be solved')

        for row in self.rows:
            for column in self.columns:
                for val in self.values:
                    if pulp.value(self.choices[val][row][column]) == 1:
                        self._sudoku.grid[row, column] = val


input_data = [
    (5, 1, 1),
    (6, 2, 1),
    (8, 4, 1),
    (4, 5, 1),
    (7, 6, 1),
    (3, 1, 2),
    (9, 3, 2),
    (6, 7, 2),
    (8, 3, 3),
    (1, 2, 4),
    (8, 5, 4),
    (4, 8, 4),
    (7, 1, 5),
    (9, 2, 5),
    (6, 4, 5),
    (2, 6, 5),
    (1, 8, 5),
    (8, 9, 5),
    (5, 2, 6),
    (3, 5, 6),
    (9, 8, 6),
    (2, 7, 7),
    (6, 3, 8),
    (8, 7, 8),
    (7, 9, 8),
    (3, 4, 9),
    (1, 5, 9),
    (6, 6, 9),
    (5, 8, 9)
]

groups = [(6, [(0, 0), (1, 0), (2, 0)]), (15, [(0, 1), (1, 1), (1, 2)]), (12, [(0, 2), (0, 3)]),
          (18, [(0, 4), (0, 5), (1, 4)]), (9, [(0, 6), (0, 7)]), (19, [(0, 8), (1, 8), (2, 8)]),
          (17, [(1, 3), (2, 3), (2, 4)]), (12, [(1, 5), (1, 6), (2, 5)]), (5, [(1, 7), (2, 7)]), (15, [(2, 1), (3, 1)]),
          (14, [(2, 2), (3, 2), (3, 3)]), (11, [(2, 6), (3, 6)]), (13, [(3, 0), (4, 0)]),
          (12, [(3, 4), (4, 4), (5, 4)]), (17, [(3, 5), (4, 5)]), (9, [(3, 7), (3, 8)]), (4, [(4, 1), (4, 2)]),
          (6, [(4, 3), (5, 3)]), (9, [(4, 6), (4, 7)]), (9, [(4, 8), (5, 8)]), (14, [(5, 0), (5, 1)]),
          (8, [(5, 2), (6, 2)]), (12, [(5, 5), (5, 6), (6, 6)]), (13, [(5, 7), (6, 7)]), (18, [(6, 0), (7, 0), (8, 0)]),
          (10, [(6, 1), (7, 1)]), (23, [(6, 3), (7, 3), (7, 2)]), (14, [(6, 4), (6, 5), (7, 5)]),
          (16, [(6, 8), (7, 8), (8, 8)]), (13, [(7, 4), (8, 4), (8, 3)]), (14, [(7, 6), (7, 7), (8, 7)]),
          (6, [(8, 1), (8, 2)]), (12, [(8, 5), (8, 6)])]
#
# sudoku = KillerSudoku()
# for total, cells in groups:
#     sudoku.add_cage(total, cells)
#
# solver = KillerSudokuSolver(sudoku)
# solver.solve()
# sudoku.print()
