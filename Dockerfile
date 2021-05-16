FROM python:3.8.7-slim

WORKDIR /tmp
COPY requirements.txt .
RUN pip3 install -r requirements.txt

WORKDIR /usr/src/app
COPY src/* ./

ENTRYPOINT ["python3", "discord_bot.py"]