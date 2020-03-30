FROM python:3.7.3

ADD . /app
WORKDIR /app

ARG FLASK_ENV="development"
ARG PORT
ARG HOST
ARG SECRET_KEY="(|9t`lmI.>F0Tj/4;DW0MV#Lkuk]A8"

ENV FLASK_ENV $FLASK_ENV
ENV SECRET_KEY $SECRET_KEY
ENV PORT $PORT
ENV HOST $HOST
ENV FLASK_APP="main.py"

EXPOSE $PORT

RUN pip3 install -r requirements.txt

CMD flask db upgrade && flask force_reseed_db && flask check_app && gunicorn -w 4 -b $HOST:$PORT --access-logfile - --error-logfile - --log-level info "main:app"
