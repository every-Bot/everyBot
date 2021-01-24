FROM python:3.6.10

RUN mkdir -p /app
WORKDIR /app

COPY requirements.txt /app
RUN pip3 install -r requirements.txt

CMD ["python3", "bin/bot.py"]