import time
import asyncio
import curses
import random
from itertools import cycle

STARS_QUANTITY = 100
TIC_TIMEOUT = 0.1
FRAME_THICKNESS = 1

SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258


async def blink(canvas, row, column, offset_tics, symbol='*'):
    """Вариант корутины с миганием звезд, когда звезды зажигаются по алгоритму
     прописанному в отдельном словаре"""

    while True:
        fonts = [
            {'font': curses.A_DIM, 'timer': offset_tics},
            {'font': curses.A_NORMAL, 'timer': 3},
            {'font': curses.A_BOLD, 'timer': 5},
            {'font': curses.A_NORMAL, 'timer': 3}]

        for coroutine_step in fonts:
            canvas.addstr(row, column, symbol, coroutine_step['font'])
            for i in range(coroutine_step['timer']):
                await asyncio.sleep(0)


async def animate_spaceship(canvas, row, column, symbol, symbol2):
    """Корутина, отрисовывающая космический корабль"""
    obstacle_right, obstacle_left, obstacle_top, obstacle_botton = calculate_obsticles(canvas, symbol)

    frames = [symbol, symbol, symbol2, symbol2]
    for frame in cycle(frames):
        draw_frame(canvas, row, column, frame)
        rows_direction, columns_direction, space_pressed = read_controls(canvas)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, frame, negative=True)

        row += rows_direction
        row = max(min(obstacle_botton, row), obstacle_top)
        column += columns_direction
        column = max(min(obstacle_right, column), int(obstacle_left))


async def fire(canvas, start_row, start_column,
               rows_speed=-0.3, columns_speed=0):
    """Корутина, отрисовывающая выстрел из корабля"""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed



async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    while row < rows_number:
        draw_frame(canvas, row, column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed


async def fill_orbit_with_garbage(canvas, garbage_variants, speed):
    first_column = 0
    last_column = curses.window.getmaxyx(canvas)[1]

    while True:
        column = random.randint(first_column, last_column)
        garbage_frame = random.choice(garbage_variants)
        coroutine_garbage = fly_garbage(canvas, column, garbage_frame, speed)
        for i in range(20):
            await asyncio.sleep(0)
        coroutines.append(coroutine_garbage)


def calculate_obsticles(canvas, symbol):
    """Функция вычисляет ограничения по экрану,
     чтобы не залетал за рамку экрана"""

    max_row = curses.window.getmaxyx(canvas)[0]
    max_column = curses.window.getmaxyx(canvas)[1]
    space_ship_rows, space_ship_columns = get_frame_size(symbol)
    obstacle_right = max_column - FRAME_THICKNESS - space_ship_columns
    obstacle_left = space_ship_columns/2 - FRAME_THICKNESS
    obstacle_botton = max_row - FRAME_THICKNESS - space_ship_rows
    obstacle_top = FRAME_THICKNESS
    return obstacle_right, obstacle_left, obstacle_top, obstacle_botton


def get_frame_size(text):
    """Функция вычисления размеров корабля"""

    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns


def draw_frame(canvas, start_row, start_column, text, negative=False):
    """Функция, которая отрисовывает объемный текст
     и может заменять один текст другим"""

    rows_number, columns_number = canvas.getmaxyx()

    for row, line in enumerate(text.splitlines(), round(start_row)):
        if row < 0:
            continue

        if row >= rows_number:
            break

        for column, symbol in enumerate(line, round(start_column)):
            if column < 0:
                continue

            if column >= columns_number:
                break

            if symbol == ' ':
                continue

            if row == rows_number - 1 and column == columns_number - 1:
                continue

            symbol = symbol if not negative else ' '
            canvas.addch(row, column, symbol)


def open_animations():
    with open("animations/spaceship_frame1.txt", "r") as frame1:
        spaceship_frame1 = frame1.read()
    with open("animations/spaceship_frame2.txt", "r") as frame2:
        spaceship_frame2 = frame2.read()
    with open('animations/duck.txt', "r") as garbage_file:
        duck = garbage_file.read()
    with open('animations/hubble.txt', "r") as garbage_file:
        hubble = garbage_file.read()
    with open('animations/lamp.txt', "r") as garbage_file:
        lamp = garbage_file.read()
    with open('animations/trash_large.txt', "r") as garbage_file:
        trash_large = garbage_file.read()
    with open('animations/trash_small.txt', "r") as garbage_file:
        trash_small = garbage_file.read()
    with open('animations/trash_xl.txt', "r") as garbage_file:
        trash_xl = garbage_file.read()

    garbage_variants = [duck, hubble, lamp, trash_large, trash_small, trash_xl]

    return spaceship_frame1, spaceship_frame2, garbage_variants


def read_controls(canvas):
    """Функция считывает нажатие клавиш вправо, влево, вниз, вверх"""

    rows_direction = columns_direction = 0
    space_pressed = False

    while True:
        canvas.nodelay(True)
        pressed_key_code = canvas.getch()

        if pressed_key_code == -1:
            break

        if pressed_key_code == UP_KEY_CODE:
            rows_direction = -1

        if pressed_key_code == DOWN_KEY_CODE:
            rows_direction = 1

        if pressed_key_code == RIGHT_KEY_CODE:
            columns_direction = 1

        if pressed_key_code == LEFT_KEY_CODE:
            columns_direction = -1

        if pressed_key_code == SPACE_KEY_CODE:
            space_pressed = True

    return rows_direction, columns_direction, space_pressed


def draw(canvas):
    """Функция, выводит все корутины на экран и запускает эмуляции игры"""

    curses.curs_set(False)
    canvas.border()
    global coroutines
    coroutines = []
    for i in range(STARS_QUANTITY):
        row = random.randint(FRAME_THICKNESS, curses.window.getmaxyx(canvas)[0] - FRAME_THICKNESS*2)
        column = random.randint(FRAME_THICKNESS, curses.window.getmaxyx(canvas)[1] - FRAME_THICKNESS*2)
        stars = ['+', '*', '.', ':']
        symbol = random.choice(stars)
        offset_tics = random.randint(10, 30)
        coroutine = blink(canvas, row, column, offset_tics, symbol)
        coroutines.append(coroutine)

    start_row = curses.window.getmaxyx(canvas)[0]/2
    start_column = curses.window.getmaxyx(canvas)[1]/2
    coroutine_fire = fire(canvas, start_row, start_column,
                          rows_speed=-0.3, columns_speed=0)
    coroutines.append(coroutine_fire)

    spaceship_frame1, spaceship_frame2, garbage_variants = open_animations()

    screen_width, screen_length = curses.window.getmaxyx(canvas)
    start_row = screen_width / 2 - 2
    start_column = screen_length / 2 - 2
    coroutine_spaceship = animate_spaceship(canvas, start_row, start_column,
                                            spaceship_frame1, spaceship_frame2)
    coroutines.append(coroutine_spaceship)

    for i in range(5):
        coroutine_garbage = fill_orbit_with_garbage(canvas, garbage_variants, speed=0.5)
        coroutines.append(coroutine_garbage)

    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        time.sleep(TIC_TIMEOUT)
        canvas.refresh()
        if not len(coroutines):
            break


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
