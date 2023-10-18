import time
import asyncio
import curses

async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await asyncio.sleep(0)
        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)
        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await asyncio.sleep(0)
        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)

def draw(canvas):
    curses.curs_set(False)
    canvas.border()
    coroutines = []
    for i in range(quantity):
        row, column = (2, 10+i*2)
        coroutine = blink(canvas, row, column)
        coroutines.append(coroutine)
    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        canvas.refresh()
        time.sleep(1)
        if not len(coroutines):
            break

if __name__ == '__main__':
    quantity = 5
    curses.update_lines_cols()
    curses.wrapper(draw)
