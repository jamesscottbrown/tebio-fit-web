#Docker file for local building and serving only
FROM ubuntu:14.04
MAINTAINER James Scott-Brown <james@jamesscottbrown.com>

RUN useradd tebiofit-user

RUN apt-get update
RUN apt-get upgrade -y

RUN apt-get install -y git python sqlite3 python-pip python-lxml
RUN pip install --upgrade pip

ADD . /code
WORKDIR /code

RUN pip install -r requirements.txt
RUN pip install gunicorn

USER tebiofit-user
ENV FLASK_APP=/code/tebio.py
ENV FLASK_DEBUG=1

CMD flask run --host=0.0.0.0