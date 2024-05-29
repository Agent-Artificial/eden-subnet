#!/bin/bash

# MIT License - Copyright (c) 2023 Bakobiibizo (https://github.com/bakobiibizo)

set -e

# Installs the Eden Subnet

echo "Installing Eden Subnet"

git clone https://github.com/agent-artificial/eden-subnet.git

cd eden-subnet &&
    export PYTHONFAULTHANDLER=1
export PYTHONUNBUFFERED=1
export PYTHONHASHSEED=random
export PIP_NO_CACHE_DIR=off
export PIP_DISABLE_PIP_VERSION_CHECK=on
export PIP_DEFAULT_TIMEOUT=100
export POETRY_NO_INTERACTION=1
export POETRY_VIRTUALENVS_CREATE=false
export POETRY_CACHE_DIR=~/.cache/pypoetry
export POETRY_HOME=~/.local/pypoetry
export POETRY_VERSION=1.8.2

RUN apt-get update &&
    apt-get install -y git curl python3-pip python3-dev python-is-python3 &&
    rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /code
COPY poetry.lock pyproject.toml /code/

RUN poetry install --only=main --no-interaction --no-ansi --no-root
COPY . /code
RUN cd websocket-client && pip install -e .
RUN cd /code && pip install -e .
