import time
import asyncio
import curses
import random

STARS_QUANTITY = 100
TIC_TIMEOUT = 0.1

'''
Вариант когда звезды зажигаются по алгоритму, с прописанием каждого шага в корутине
'''
# async def blink(canvas, row, column, symbol='*'):
#     while True:
#         canvas.addstr(row, column, symbol, curses.A_DIM)
#         for i in range(random.randint(10, 30)):
#             await asyncio.sleep(0)
#
#         canvas.addstr(row, column, symbol)
#         for i in range(3):
#             await asyncio.sleep(0)
#
#         canvas.addstr(row, column, symbol, curses.A_BOLD)
#         for i in range(5):
#             await asyncio.sleep(0)
#
#         canvas.addstr(row, column, symbol)
#         for i in range(3):
#             await asyncio.sleep(0)


'''
Вариант когда звезды зажигаются по алгоритму прописанному в отдельном словаре
'''
async def blink(canvas, row, column, symbol='*'):
    while True:
        fonts = [
            {'font': curses.A_DIM, 'timer': random.randint(10, 30)},
            {'font': curses.A_NORMAL, 'timer': 3},
            {'font': curses.A_BOLD, 'timer': 5},
            {'font': curses.A_NORMAL, 'timer': 3}]

        for coroutine_step in fonts:
            canvas.addstr(row, column, symbol, coroutine_step['font'])
            for i in range(coroutine_step['timer']):
                await asyncio.sleep(0)


def draw(canvas):
    curses.curs_set(False)
    canvas.border()
    coroutines = []
    for i in range(STARS_QUANTITY):
        row = random.randint(1, curses.window.getmaxyx(canvas)[0] - 2)
        column = random.randint(1, curses.window.getmaxyx(canvas)[1] - 2)
        stars = ['+', '*', '.', ':']
        symbol = random.choice(stars)
        coroutine = blink(canvas, row, column, symbol)
        coroutines.append(coroutine)
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
