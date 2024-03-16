import os
import random
import textwrap
import threading
import time
from datetime import datetime
from threading import Semaphore
import requests
import schedule
import urllib3
from PIL import Image, ImageDraw, ImageFont

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
API_URL = os.environ.get('API_URL')
api_token = os.environ.get("API_TOKEN")
current_directory = os.path.dirname(__file__)

lock = Semaphore(2)


class Generator:
    def __init__(self, holiday, work_file_name):
        self.WX_H = 3000
        self.FONT_SIZE = 90
        self.TEXT_INTERVAL = 100

        self.work_file_name = work_file_name

        self.holiday = holiday
        self.result_gif = None
        self.gif_frame = self.get_random_file("/assets/frames/")
        self.jpeg_path = self.get_random_file("/assets/template_pic/")
        self.gif_kitty = self.get_random_file("/assets/kitty/")
        self.gif_flowers = self.get_random_file("/assets/flowers/")
        self.gif_decal = self.get_random_file("/assets/special_effects/")
        self.run()

    @staticmethod
    def get_random_file(path):
        return current_directory + path + random.choice(os.listdir(current_directory + path))

    def save_frames(self, frames) -> str:
        frames[0].save(f'gif_{self.work_file_name}.gif',
                       save_all=True,
                       append_images=frames[1:],
                       optimize=True,
                       duration=100,
                       loop=0)
        return current_directory + f'/gif_{self.work_file_name}.gif'

    def overlay_frames(self, gif_path: str, jpg_path: str) -> Image:
        frames = []
        with Image.open(gif_path) as gif_img, Image.open(jpg_path) as jpeg_img:
            try:
                while True:
                    current_frame = gif_img.tell()

                    jpeg_rgba = jpeg_img.convert("RGBA").resize(size=(400, 400))
                    gif_frame_rgba = gif_img.copy().convert("RGBA")
                    combined_img = Image.new("RGBA", gif_frame_rgba.size)

                    combined_img.paste(jpeg_rgba, (0, 0), jpeg_rgba)
                    combined_img.paste(gif_frame_rgba, (0, 0), gif_frame_rgba)

                    frames.append(combined_img)
                    gif_img.seek(current_frame + 1)
            except EOFError:
                pass
            self.save_frames(frames)
        return Image.open(f"gif_{self.work_file_name}.gif")

    def overlay_gifs(self, background_gif: Image, foreground_gif_path: str, size=None, position=(0, 0)) -> Image:
        frames = []
        with background_gif, Image.open(foreground_gif_path) as foreground_gif:
            try:
                while True:
                    back_gif_frame = background_gif.tell()
                    front_gif_frame = foreground_gif.tell()

                    gif_frame_background = background_gif.copy().convert("RGBA")
                    gif_frame_foreground = foreground_gif.copy().convert("RGBA")

                    combined_img = Image.new("RGBA", gif_frame_background.size)
                    combined_img.paste(gif_frame_background, (0, 0), gif_frame_background)
                    if size is not None:
                        combined_img.paste(gif_frame_foreground.resize(size=size),
                                           box=position,
                                           mask=gif_frame_foreground.resize(size=size))
                    else:
                        combined_img.paste(gif_frame_foreground, box=position, mask=gif_frame_foreground)

                    frames.append(combined_img)

                    background_gif.seek(back_gif_frame + 1)
                    foreground_gif.seek(front_gif_frame + 1)
            except EOFError:
                pass
            self.save_frames(frames)
        return Image.open(f"gif_{self.work_file_name}.gif")

    def add_text_to_gif(self, gif: Image, holiday: str) -> None:
        frames = []
        width, height = gif.size
        font = ImageFont.truetype(os.path.join(current_directory + r"/font.otf"),
                                  int(self.FONT_SIZE * (width + height) / self.WX_H), encoding='UTF-8')

        try:
            while True:
                margin = offset = 35
                current_frame = gif.tell()
                gif_frame_rgba = gif.copy().convert("RGBA")
                img = Image.new("RGBA", gif.size)

                img.paste(gif_frame_rgba)
                drawer = ImageDraw.Draw(img)

                for line in textwrap.wrap("С праздником!\nСегодня " + holiday, width=margin):
                    bbox = drawer.textbbox((0, 0), line, font=font)
                    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
                    drawer.text(((width - w) / 2, (height - h + offset) / 2), line, font=font, fill="white",
                                stroke_width=2, stroke_fill="black")
                    offset += h + int(self.TEXT_INTERVAL * (width + height) / self.WX_H)

                frames.append(img)
                gif.seek(current_frame + 1)
        except EOFError:
            pass

        gif.close()
        self.save_frames(frames)
        self.result_gif = f"gif_{self.work_file_name}.gif"
        self.upload_photo()

    def upload_photo(self) -> None:
        url = API_URL + "api/v2/pictures/upload_files"
        gif_name = random.choice(range(1000000000000))
        with open(self.result_gif, 'rb') as gif:
            body = {'token': api_token,
                    "gif_name": str(gif_name)}
            payload = {"gif": gif}
            requests.post(url, data=body, files=payload, verify=False)

        os.remove(self.result_gif)
        lock.release()

    def run(self):
        lock.acquire()
        with_frame = self.overlay_frames(
            self.gif_frame,
            self.jpeg_path)
        with_kitty = self.overlay_gifs(
            with_frame,
            self.gif_kitty,
            size=(101, 101), position=(15, 284))
        with_flowers = self.overlay_gifs(
            with_kitty,
            self.gif_flowers,
            size=(101, 101), position=(284, 15))
        with_decal = self.overlay_gifs(
            with_flowers,
            self.gif_decal,
            size=(400, 400))
        self.add_text_to_gif(with_decal, self.holiday.replace("•", ""))


def run_postcard_generator() -> None:
    """КТО ЕСЛИ НЕ Я БУДЕТ ЗАНИМАТЬСЯ ТАКОЙ ХУЙНЕЙ?"""

    requests.post(API_URL + 'api/v2/pictures/delete', data={'token': api_token}, verify=False)

    year, month, day = datetime.now().year, datetime.now().month, datetime.now().day
    holidays_list = requests.post(API_URL + 'api/v2/get_by_date',
                                  data={'token': api_token, 'date': f'{year}-{month}-{day}'}, verify=False)

    threads = []

    for holiday in holidays_list.json():
        thread = threading.Thread(target=Generator(holiday, random.choice(range(10000))).run)
        threads.append(thread)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()


def scheduler():
    run_postcard_generator()
    schedule.every().day.at("00:00").do(run_postcard_generator)
    while 1:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    scheduler()
