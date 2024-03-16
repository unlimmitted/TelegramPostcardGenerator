FROM python:3.11
ENV BOT_TOKEN=""
ENV API_URL=""
ENV API_TOKEN=""

COPY .. /HolidayApp/.
RUN pip install --upgrade pip
RUN pip install -r /HolidayApp/requirements.txt