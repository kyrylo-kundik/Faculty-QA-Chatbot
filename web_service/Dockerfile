FROM python:3.7.3

ADD . /app
WORKDIR /app

ARG FLASK_ENV="production"
ARG PORT
ARG HOST
ARG SECRET_KEY="(|9t`lmI.>F0Tj/4;DW0MV#Lkuk]A8"

ENV FLASK_ENV $FLASK_ENV
ENV SECRET_KEY $SECRET_KEY
ENV PORT $PORT
ENV HOST $HOST

EXPOSE $PORT

RUN pip3 install -r requirements.txt
RUN pip3 install gunicorn

CMD gunicorn -w 4 -b $HOST:$PORT "run:create_app()"
