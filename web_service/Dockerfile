FROM python:3.7.3

ADD . /app
WORKDIR /app

ARG MODEL_PATH="app/qas/model"
RUN mkdir $MODEL_PATH
RUN curl -o $MODEL_PATH/model.zip https://storage.googleapis.com/bert_models/2018_11_23/multi_cased_L-12_H-768_A-12.zip && unzip -j $MODEL_PATH/model.zip && rm -f $MODEL_PATH/model.zip

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

#ADD https://storage.googleapis.com/bert_models/2018_11_23/multi_cased_L-12_H-768_A-12.zip app/qas/model/

CMD flask db upgrade && gunicorn -w 4 -b $HOST:$PORT "main:app"
