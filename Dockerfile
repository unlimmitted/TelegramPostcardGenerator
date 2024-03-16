FROM python:3.11
ENV BOT_TOKEN=""
ENV API_URL=""
ENV API_TOKEN=""

RUN mkdir HolidayBot
COPY . /HolidayBot/.
RUN pip install --upgrade pip
RUN pip install -r /HolidayBot/requirements.txt

CMD ["python", "/HolidayBot/main.py"]