# this containerfile is only for testing purposes


FROM fedora:latest

# here will be the copied files from alpa
WORKDIR /alpa/alpa_copy
COPY . /alpa/alpa_copy

# bind local alpa project to this directory to tinker with it
RUN mkdir -p /alpa/alpa_bind

RUN dnf install -y make git pip poetry
# install package dependencies (first enter poetry shell -> `$ poetry shell`)
RUN poetry install
