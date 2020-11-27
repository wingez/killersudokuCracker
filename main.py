from dataclasses import dataclass
from tempfile import TemporaryDirectory
import shutil
from typing import Tuple, List

from PIL import Image
import numpy as np

import cv2

import pytesseract

CELL_SIZE = 72

# cv2.num
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'


def remove_grid(array):
    # remove left and top bar
    data[0:6, :] = 0
    data[:, 0:6] = 0

    far = 6 + 72 * 9 + 4 * 8
    data[far:far + 6, :] = 0
    data[:, far:far + 6] = 0

    for i in range(8):
        j = 6 + 72 * (i + 1) + 4 * i

        # remove horizontal line
        array[j:j + 4, :] = 0
        # remove vertical line
        array[:, j:j + 4] = 0


def get_coord_for_cell(y, x):
    return 6 + y * (72 + 4), 6 + x * (72 + 4)


def get_coords_jagged_cell(y, x):
    y1, x1 = get_coord_for_cell(y, x)
    return y1 + 2, x1 + 2


def get_coords_inner_cell(y, x):
    y1, x1 = get_coords_jagged_cell(y, x)
    return y1 + 2, x1 + 2


def get_number_box(arr, y, x):
    y1, x1 = get_coords_inner_cell(y, x)

    return arr[y1:y1 + 25, x1:x1 + 25]


def get_value_of_cell(arr, y, x):
    digit_image = Image.fromarray(get_number_box(arr, y, x)).convert('RGBA')

    new_image = Image.new("RGBA", digit_image.size, "WHITE")
    new_image.paste(digit_image, (5, 5), digit_image)
    new_image.convert('RGB')
    new_image = new_image.resize((50, 50), Image.ANTIALIAS)

    ret, img = cv2.threshold(np.array(new_image), 125, 255, cv2.THRESH_BINARY)
    img = Image.fromarray(img)
    # new_image.show()
    v = pytesseract.image_to_string(img, config='--psm 13 digits').strip()

    return int(v) if v else 0


def get_walls(arr, y, x):
    top, left = get_coords_jagged_cell(y, x)
    right = left + 68
    bottom = top + 68

    return (np.sum(arr[top:top + 2, right - 25:right - 5]) > 0,
            np.sum(arr[bottom - 25:bottom - 5, left:left + 5]) > 0)


@dataclass
class Group:
    sum: int
    cells: List[Tuple[int, int]]


def find_groups(arr) -> List[Group]:
    @dataclass
    class CanIGoTo:
        right: bool = False
        left: bool = False
        up: bool = False
        down: bool = False

    cells = [[CanIGoTo() for _ in range(9)] for _ in range(9)]
    for y in range(9):
        for x in range(9):
            wall_up, wall_left = get_walls(arr, y, x)
            if not wall_up:
                cells[y][x].up = True
                if y > 0:
                    cells[y - 1][x].down = True
            if not wall_left:
                cells[y][x].left = True
                if x > 0:
                    cells[y][x - 1].right = True

    def add_to_group(group: List[Tuple[int, int]], y: int, x: int):
        group.append((y, x))
        v = cells[y][x]
        if v.right and (y, x + 1) not in group:
            add_to_group(group, y, x + 1)
        if v.left and (y, x - 1) not in group:
            add_to_group(group, y, x - 1)
        if v.up and (y - 1, x) not in group:
            add_to_group(group, y - 1, x)
        if v.down and (y + 1, x) not in group:
            add_to_group(group, y + 1, x)

    groups: List[List[Tuple[int, int]]] = []
    for y in range(9):
        for x in range(9):

            if not any((y, x) in group for group in groups):
                current = []
                add_to_group(current, y, x)

                groups.append(current)

    result = []

    for index, group in enumerate(groups, start=1):
        for cell in group:
            y, x = cell
            val = get_value_of_cell(arr, y, x)
            if val > 0:
                result.append(Group(val, group))
                break
        else:
            raise ValueError

    a = np.zeros((9, 9))
    for group in result:
        for y, x in group.cells:
            a[y, x] = group.sum

    print('groups')
    print(a)
    print()
    if sum(group.sum for group in result) != 45*9:
        raise ValueError

    return result


shutil.copy('index.png', 'temp.png')

image = Image.open('temp.png')

print(image.format)
print(image.size)
print(image.mode)
data = np.array(image.convert('LA'))
remove_grid(data)

groups = find_groups(data)

board = np.zeros((9, 9))
import solver

print('starting solving')
s = solver.Solver(board, groups)
s.solve()

print('solved')
print(board)

# result_image = Image.fromarray(data)
