FROM python:3.12-slim

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt
ENTRYPOINT [ "python3", "main.py" ]