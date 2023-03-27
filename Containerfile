FROM python:3.11-alpine

ENV PYTHONBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /alpa-conf/alpa-conf_copied

RUN apk add bash

RUN pip install --upgrade pip
RUN pip install poetry

COPY . .
RUN poetry install

WORKDIR /alpa-conf
