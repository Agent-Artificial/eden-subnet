FROM python:3.10-slim

ENV PYTHONFAULTHANDLER=1 \
PYTHONUNBUFFERED=1 \
PYTHONHASHSEED=random \
PIP_NO_CACHE_DIR=off \
PIP_DISABLE_PIP_VERSION_CHECK=on \
PIP_DEFAULT_TIMEOUT=100 

RUN apt-get update && \
    apt-get install -y bash python3 python3-venv python3-pip python3-dev python-is-python3 build-essential git  && \
    rm -rf /var/lib/apt/lists/*

COPY .venv /code/.venv
COPY . /code
WORKDIR /code

RUN pip install git+https://github.com/agicommies/communex

RUN pip install -r requirements.txt











