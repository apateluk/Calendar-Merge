# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt

RUN apt-get update && apt-get install -y git

RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python3", "-m" ,"calmerge"]