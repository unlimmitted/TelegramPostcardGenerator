FROM python:3.11
ENV TZ="Europe/Moscow"
ENV API_URL=""
ENV API_TOKEN=""
WORKDIR HolidayApp
RUN mkdir generator
COPY .. generator/.
RUN pip install --upgrade pip
RUN pip install -r generator/requirements.txt