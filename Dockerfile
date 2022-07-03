# syntax=docker/dockerfile:1
FROM python:3.10.2

WORKDIR /
COPY requirements.txt requirements.txt
RUN apt-get update
RUN pip3 install -r requirements.txt

COPY . .
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]