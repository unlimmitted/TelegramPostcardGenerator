import os
import random

import requests
import urllib3
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
BOT_TOKEN = os.environ.get('BOT_TOKEN')
global_url = os.environ.get('API_URL')
api_key = os.environ.get("API_TOKEN")

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer('<b>Ку</b>\n<i>Напиши в любом диалоге "@what_holiday_today_bot "</i>', parse_mode='html')


@dp.inline_handler()
async def on_inline_query(query: types.InlineQuery):
    offset = int(query.offset) if query.offset else 0

    pic = requests.post(global_url + 'api/v2/pictures/get_image_names', data={'token': api_key}, verify=False).json()

    preload_count = 10
    results = []

    for i, image in enumerate(pic[offset:offset + preload_count], start=offset):
        result_id = str(random.randint(1, 100000000))
        result = types.InlineQueryResultGif(
            id=result_id,
            gif_url=global_url + 'api/v2/pictures/' + image,
            thumb_url=global_url + 'api/v2/pictures/' + image,
        )
        results.append(result)

    next_offset = offset + preload_count
    await bot.answer_inline_query(query.id, results, cache_time=0, next_offset=str(next_offset))


if __name__ == '__main__':
    while True:
        try:
            executor.start_polling(dp, skip_updates=True)
        except Exception as error:
            print(error)
