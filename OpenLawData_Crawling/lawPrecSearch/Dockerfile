FROM python:3.7.1-slim
LABEL maintainer="Yoon-Su Choi <yunsu246@gmail.com>"

USER root

ENV APP_DIR /tmp

WORKDIR $APP_DIR

COPY requirements.txt .
COPY lib ./lib
COPY src ./src

ENV PYTHONPATH /tmp/src:/tmp/lib

VOLUME ./src/:/tmp/src/

RUN mkdir -p $APP_DIR/lib
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt -t $APP_DIR/lib

CMD ["python3", "src/main.py"]
