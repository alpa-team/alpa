# this containerfile is only for testing purposes


FROM fedora:latest

WORKDIR /alpa_workdir

COPY . /alpa_workdir

RUN dnf install -y make git pip poetry
RUN poetry install
