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
        self.problem += (0, "Arbitrary Objective Function")
        self.choices = pulp.LpVariable.dicts(
            "Choice", (self.values, self.rows, self.columns), cat=pulp.const.LpBinary
        )

    def _apply_sudoku_constraints(self):
        # One digit per cell
        for row in self.rows:
            for column in self.columns:
                self.problem += pulp.lpSum([self.choices[v][row][column] for v in self.values]) <= 1

        # Each digit one time per row/column/box
        for value in self.values:
            for row in self.rows:
                self.problem += pulp.lpSum([self.choices[value][row][column] for column in self.columns]) <= 1

            for column in self.columns:
                self.problem += pulp.lpSum([self.choices[value][row][column] for row in self.rows]) <= 1

            boxes = [
                [(row, column) for row in range(i, i + 3) for column in range(j, j + 3)]
                for i in range(0, 9, 3) for j in range(0, 9, 3)
            ]

            for box in boxes:
                self.problem += pulp.lpSum([self.choices[value][row][column] for row, column in box]) <= 1

    def _apply_cage_constraints(self):
        for cage in self._sudoku.cages:
            constraints = [
                self.choices[val][row][column] * val for row, column in cage.cells for val in self.values
            ]
            # Cage should sum to value
            self.problem += pulp.lpSum(constraints) >= cage.sum

            # Value at most one time per cage
            for value in self.values:
                self.problem += pulp.lpSum([self.choices[value][row][column] for row, column in cage.cells]) <= 1

    def solve(self):
        self._apply_sudoku_constraints()
        self._apply_cage_constraints()

        self.problem.solve()  # pulp.getSolver('PULP_CHOCO_CMD'))
        if not self.problem.status == 1:
            raise AssertionError('Sudoku could not be solved')

        for row in self.rows:
            for column in self.columns:
                for val in self.values:
                    if pulp.value(self.choices[val][row][column]) == 1:
                        self._sudoku.grid[row, column] = val
