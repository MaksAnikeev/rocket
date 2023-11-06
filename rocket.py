import asyncio
import curses
import random
import time
from itertools import cycle

from actions_with_frames import draw_frame, get_frame_size
from explosion import explode
from obstacles import Obstacle
from physics import update_speed

STARS_QUANTITY = 100
TIC_TIMEOUT = 0.1
FRAME_THICKNESS = 1

SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258

obstacles = []
coroutines = []
obstacles_in_last_collisions = []

year = 1956

PHRASES = {
    1957: "First Sputnik",
    1961: "Gagarin  flew!",
    1969: "Armstrong got on the moon!",
    1971: "First orbital space station Salute-1",
    1981: "Flight of the Shuttle Columbia",
    1998: 'ISS start building',
    2011: 'Messenger launch to Mercury',
    2020: "Take the plasma gun! Shoot the garbage!",
}


async def sleep(tics=1):
    """Корутина, которая задает временные промежутки
     при запуске других корутин"""

    for i in range(tics):
        await asyncio.sleep(0)


async def show_year(canvas, row, column):
    """Корутина, которая отсчитывает годы"""
    global year
    while True:
        canvas.addstr(row, column, f'Year now - {year}')
        await sleep(tics=20)
        year += 1


async def show_print(canvas, row, column):
    """Корутина, которая показывает события"""
    global year
    column_print = 0
    while True:
        if year < 1957:
            await asyncio.sleep(0)
        elif year in PHRASES.keys():
            phrase = f'{PHRASES[year]}'
            draw_frame(canvas, row, column_print, phrase, negative=True)
            column_print = int(column - len(PHRASES[year])/2)
            draw_frame(canvas, row, column_print, phrase)
            await sleep(tics=5)
        else:
            draw_frame(canvas, row, column_print, phrase)
            await asyncio.sleep(0)


async def blink(canvas, row, column, offset_tics, symbol='*'):
    """Корутина с миганием звезд, звезды зажигаются по алгоритму
     прописанному в отдельном словаре"""

    while True:
        fonts = [
            {'font': curses.A_DIM, 'timer': offset_tics},
            {'font': curses.A_NORMAL, 'timer': 3},
            {'font': curses.A_BOLD, 'timer': 5},
            {'font': curses.A_NORMAL, 'timer': 3}]

        for coroutine_step in fonts:
            canvas.addstr(row, column, symbol, coroutine_step['font'])
            await sleep(tics=coroutine_step['timer'])


async def animate_spaceship(canvas, row, column, symbol, symbol2):
    """Корутина, отрисовывающая космический корабль"""

    obstacle_right, obstacle_left, obstacle_top, obstacle_bottom = calculate_obstacles(canvas, symbol)

    frames = [symbol, symbol, symbol2, symbol2]
    row_speed = column_speed = 0
    obj_size_rows, obj_size_columns = get_frame_size(symbol)
    for frame in cycle(frames):
        draw_frame(canvas, row, column, frame)
        rows_direction, columns_direction, space_pressed = read_controls(canvas)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, frame, negative=True)

        row_speed, column_speed = run_speed(rows_direction, columns_direction,
                                            row_speed, column_speed)
        row += rows_direction
        row += row_speed
        row = max(min(obstacle_bottom, row), obstacle_top)

        column += columns_direction
        column += column_speed
        column = max(min(obstacle_right, column), int(obstacle_left))

        if space_pressed and year >= 2020:
            start_row = row + 2
            start_column = column + 2
            coroutine_fire = fire(canvas, start_row, start_column,
                                  rows_speed=-0.3, columns_speed=0)
            coroutines.append(coroutine_fire)

        for obstacle in obstacles:
            if obstacle.has_collision(row, column, obj_size_rows, obj_size_columns):
                await explode(canvas, row + obj_size_rows / 2,
                              column + obj_size_columns / 2)
                screen_width, screen_length = curses.window.getmaxyx(canvas)
                row = screen_width / 4 + screen_width / 5
                column = screen_length / 3
                game_over = open_animations()[3]
                coroutine_game_over = show_game_over(canvas, row, column, text=game_over)
                coroutines.append(coroutine_game_over)
                return


async def show_game_over(canvas, row, column, text):
    """Корутина, отрисовывающая GAME OVER"""
    while True:
        draw_frame(canvas, row, column, text)
        await asyncio.sleep(0)


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
        for obstacle in obstacles:
            if obstacle.has_collision(row, column):
                obstacles_in_last_collisions.append(obstacle)
                # return


async def fly_garbage(canvas, garbage_object, column, row=0, speed=0.5):
    """Анимируйте мусор, летящий сверху вниз.
    Положение столбца останется таким же, как указано при запуске."""

    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    garbage_rows, garbage_columns = get_frame_size(garbage_object)
    obstacle = Obstacle(row, column, garbage_rows, garbage_columns, garbage_object)
    obstacles.append(obstacle)
    while row < rows_number:
        draw_frame(canvas, row, column, garbage_object)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_object, negative=True)
        row += speed
        obstacle.row = row
        if obstacle in obstacles_in_last_collisions:
            await explode(canvas, row+garbage_rows/2, column+garbage_columns/2)
            obstacles_in_last_collisions.remove(obstacle)
            return
        if row == rows_number:
            obstacles.remove(obstacle)


async def fill_orbit_with_garbage(canvas, garbage_variants, speed):
    """Функция запускает корутины создания мусора по циклу"""

    first_column = 0
    last_column = curses.window.getmaxyx(canvas)[1]

    while True:
        column = random.randint(first_column, last_column)
        row = 0
        garbage_object = random.choice(garbage_variants)

        if get_garbage_delay_tics(year):
            coroutine_garbage = fly_garbage(canvas, garbage_object, column, row, speed)
            time_break = get_garbage_delay_tics(year)
            await sleep(time_break*2)
            coroutines.append(coroutine_garbage)
        await asyncio.sleep(0)


def run_speed(rows_direction, columns_direction, row_speed, column_speed):
    """Функция ускоряет или замедляет движение корабля
     при нажатии клавиш управления"""

    if rows_direction < 0:
        row_speed, column_speed = update_speed(row_speed, column_speed, -1, 0)
    if rows_direction == 0:
        row_speed, column_speed = update_speed(row_speed, column_speed, 0, 0)
    if rows_direction > 0:
        row_speed, column_speed = update_speed(row_speed, column_speed, 1, 0)

    if columns_direction < 0:
        row_speed, column_speed = update_speed(row_speed, column_speed, 0, -1)
    if columns_direction == 0:
        row_speed, column_speed = update_speed(row_speed, column_speed, 0, 0)
    if columns_direction > 0:
        row_speed, column_speed = update_speed(row_speed, column_speed, 0, 1)

    return row_speed, column_speed


def get_garbage_delay_tics(year):
    """Функция уменьшает промежутки между падением мусора,
     усложняя скорость игры"""

    if year < 1961:
        return None
    elif year < 1969:
        return 20
    elif year < 1981:
        return 14
    elif year < 1995:
        return 10
    elif year < 2010:
        return 8
    elif year < 2020:
        return 6
    else:
        return 2


def calculate_obstacles(canvas, symbol):
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


def open_animations():
    """Функция открывает файлы для работы функции draw_frame"""

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
    with open('animations/game_over.txt', "r", encoding="utf8") as game_over_file:
        game_over = game_over_file.read()

    garbage_variants = [duck, hubble, lamp, trash_large, trash_small, trash_xl]
    return spaceship_frame1, spaceship_frame2, garbage_variants, game_over


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
    screen_width, screen_length = curses.window.getmaxyx(canvas)
    for i in range(STARS_QUANTITY):
        row = random.randint(FRAME_THICKNESS,
                             curses.window.getmaxyx(canvas)[0] - FRAME_THICKNESS*2)
        column = random.randint(FRAME_THICKNESS,
                                curses.window.getmaxyx(canvas)[1] - FRAME_THICKNESS*2)
        stars = ['+', '*', '.', ':']
        symbol = random.choice(stars)
        offset_tics = random.randint(10, 30)
        coroutine = blink(canvas, row, column, offset_tics, symbol)
        coroutines.append(coroutine)

    coroutine_year = show_year(canvas, row=screen_width-2, column=screen_length-20)
    coroutines.append(coroutine_year)

    coroutine_print = show_print(canvas,
                                 row=screen_width - 2,
                                 column=screen_length/2)
    coroutines.append(coroutine_print)

    spaceship_frame1, spaceship_frame2, garbage_variants, game_over = open_animations()

    start_row = screen_width / 2 - 2
    start_column = screen_length / 2 - 2
    coroutine_spaceship = animate_spaceship(canvas, start_row, start_column,
                                            spaceship_frame1, spaceship_frame2)
    coroutines.append(coroutine_spaceship)

    coroutine_garbage = fill_orbit_with_garbage(canvas, garbage_variants, speed=0.2)
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
