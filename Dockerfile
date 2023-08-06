# Use an official Python runtime as a parent image
FROM python:latest

# Set the working directory to /app
WORKDIR /app

# see also https://izziswift.com/integrating-python-poetry-with-docker/
ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.5.0

RUN pip3 install --upgrade pip wheel setuptools "poetry==$POETRY_VERSION"

COPY src/poetry.lock src/pyproject.toml /app/

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

# Copy the current directory contents into the container at /app
COPY . /app

CMD uvicorn main:app --reload --host 0.0.0.0 --port 8000
