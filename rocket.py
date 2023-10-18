import time
import asyncio
import curses


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for i in range(20):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for i in range(3):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for i in range(5):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for i in range(3):
            await asyncio.sleep(0)


        # shrifts = [{'shrift':curses.A_DIM, 'timer': 2},
        #           {'shrift': '', 'timer': 0.3},
        #           {'shrift': curses.A_BOLD, 'timer': 0.5},
        #           {'shrift': '', 'timer': 0.3}]
        # for number, coroutine_step in enumerate(shrifts):
        #     if coroutine_step['shrift']:
        #         canvas.addstr(row, column, f'{number}', coroutine_step['shrift'])
        #         await asyncio.sleep(0)
        #     else:
        #         canvas.addstr(row, column, f'{number}')
        #         await asyncio.sleep(0)
        #     time.sleep(coroutine_step['timer']/stars_quantity)
        #     await asyncio.sleep(0)


def draw(canvas):
    curses.curs_set(False)
    canvas.border()
    coroutines = []
    for i in range(stars_quantity):
        row, column = (2, 2+i*2)
        coroutine = blink(canvas, row, column)
        coroutines.append(coroutine)
    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        time.sleep(0.1)
        canvas.refresh()
        if not len(coroutines):
            break

if __name__ == '__main__':
    stars_quantity = 20
    curses.update_lines_cols()
    curses.wrapper(draw)
