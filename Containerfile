# this containerfile is only for testing purposes


FROM fedora:latest

WORKDIR /alpa_workdir

COPY . /alpa_workdir

RUN dnf install -y make git pip
RUN curl -sSL https://install.python-poetry.org | python3 -
RUN export PATH="/root/.local/bin:$PATH"
