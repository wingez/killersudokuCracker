import asyncio
import base64
import io
import shutil
import time
from dataclasses import dataclass
import random
from typing import Tuple, List, Dict
from pathlib import Path

# import cv2
import numpy as np
# import pytesseract
from PIL import Image, ImageChops
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.webdriver import WebDriver
from webdriver_manager.firefox import GeckoDriverManager

from temp import KillerSudoku

CELL_SIZE = 72

# cv2.num

digitsfolder = Path('digitimages')

digitsimages: List[Tuple[Image.Image, int]] = []

for path in digitsfolder.iterdir():
    image = Image.open(path)
    name = path.stem
    digitsimages.append((image, int(name)))


def remove_grid(array):
    # remove left and top bar
    array[0:6, :] = 0
    array[:, 0:6] = 0

    far = 6 + 72 * 9 + 4 * 8
    array[far:far + 6, :] = 0
    array[:, far:far + 6] = 0

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

    for image, digit in digitsimages:
        if not ImageChops.difference(digit_image, image).getbbox():
            return digit

    digit_image.save(str(digitsfolder / f'renameme{random.randint(0, 10000)}.png'))
    return 0

    if digit_image in imagemap:
        return imagemap[digit_image]

    new_image = Image.new("RGBA", digit_image.size, "WHITE")
    new_image.paste(digit_image, (5, 5), digit_image)
    new_image.convert('RGB')
    new_image = new_image.resize((50, 50), Image.ANTIALIAS)

    # ret, img = cv2.threshold(np.array(new_image), 125, 255, cv2.THRESH_BINARY)
    # img = Image.fromarray(img)
    # new_image.show()
    # v = pytesseract.image_to_string(new_image, config='--psm 13 digits').strip()

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
            pass
            # raise ValueError

    print([(g.sum, g.cells) for g in result])

    a = np.zeros((9, 9))
    for group in result:
        for y, x in group.cells:
            a[y, x] = group.sum

    print('groups')
    print(a)
    print()
    if sum(group.sum for group in result) != 45 * 9:
        raise AssertionError('Sum of cages does not sum to 45*9 ')

    return result


async def main(puzzle_number: int):
    driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())

    try:
        await asyncio.sleep(5)
        driver.get(f'http://www.dailykillersudoku.com/puzzle/{puzzle_number}')

        img_data = driver.execute_script('return document.getElementsByClassName("puzzle-canvas")[0].toDataURL()')

        sudoku, _ = await asyncio.gather(
            asyncio.to_thread(solve_killer_sudoku_from_image_data, img_data),
            asyncio.to_thread(prepare_browser, driver)

        )

        enter_solution(driver, sudoku)

    finally:
        driver.close()


def solve_killer_sudoku_from_image_data(data: str) -> KillerSudoku:
    image = Image.open(io.BytesIO(base64.b64decode(data.split(',')[1])))
    # image.show()
    image.save('temp.png')
    shutil.copy('index.png', 'temp.png')

    # image = Image.open('temp.png')

    print(image.format)
    print(image.size)
    print(image.mode)
    data = np.array(image.convert('LA'))
    remove_grid(data)

    sudoku = KillerSudoku()

    groups = find_groups(data)

    for group in groups:
        sudoku.add_cage(group.sum, group.cells)

    sudoku.print()
    sudoku.solve()
    sudoku.print()

    print('solved')
    return sudoku


def prepare_browser(driver: WebDriver):
    driver.find_element_by_id('ez-accept-all').click()
    driver.find_element(By.XPATH, '//a[.="Sign in"]').click()
    driver.implicitly_wait(3)
    driver.find_element_by_id('user_email').send_keys('tibbetobbe8@gmail.com')
    driver.find_element_by_id('user_password').send_keys('UB9qgf38N8akN2f')
    driver.find_element_by_id('user_password').send_keys(Keys.ENTER)
    time.sleep(5)
    driver.find_element(By.XPATH, '//span[.="Start Again"]').click()
    try:
        driver.find_element(By.XPATH, '//button[.="Yes"]').click()
    except NoSuchElementException:
        pass

    time.sleep(3)


def enter_solution(driver: WebDriver, sudoku: KillerSudoku):
    first_cell = driver.find_elements_by_class_name('cell')[0]
    ActionChains(driver).move_to_element(first_cell).click().perform()
    time.sleep(1)

    def press_key(key):
        ActionChains(driver).send_keys(key).perform()

    for row in range(9):
        for column in range(9):
            press_key(str(int(sudoku.grid[row, column])))
            time.sleep(0.03)

            press_key(Keys.ARROW_RIGHT)
            time.sleep(0.03)

        press_key(Keys.ARROW_DOWN)
        time.sleep(0.03)

    time.sleep(2)
    driver.find_element(By.XPATH, '//button[.="Back to the puzzles"]').click()


if __name__ == '__main__':
    import sys

    for puzzle in sys.argv[1:]:
        asyncio.run(main(int(puzzle)))
