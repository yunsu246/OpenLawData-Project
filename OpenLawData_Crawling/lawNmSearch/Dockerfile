FROM lambci/lambda:python3.6
LABEL maintainer="Yoon-Su Choi <yunsu246@gmail.com>"

USER root

ENV APP_DIR /var/task

WORKDIR $APP_DIR

COPY requirements.txt .
COPY lib ./lib

RUN mkdir -p $APP_DIR/lib
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt -t /var/task/lib
