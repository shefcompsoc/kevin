FROM python:3.12.7-bullseye

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt
ENTRYPOINT [ "python", "main.py" ]