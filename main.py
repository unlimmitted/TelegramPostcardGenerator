from threading import Thread

import nest_asyncio

from bot import bot
from generator import generator

nest_asyncio.apply()


def thread_initiation():
    threads = [Thread(target=bot.run), Thread(target=generator.scheduler)]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()


if __name__ == '__main__':
    thread_initiation()
