# Use the official Python 3.9 image as the base image
FROM python:3.11

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install necessary system packages
RUN echo "deb http://deb.debian.org/debian bookworm main" >> /etc/apt/sources.list && \
    apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc libmagic1 sqlite3 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry

# Set the working directory
WORKDIR /app

# Copy the pyproject.toml and poetry.lock files
COPY pyproject.toml poetry.lock /app/

# Install the project dependencies
RUN poetry config virtualenvs.create false && \
    poetry install

# Copy the rest of the application code
COPY . /app/

RUN chmod +x wait-for-it.sh
RUN chmod +x entrypoint.sh

# Default command to start the application
CMD python manage.py migrate && python -m gunicorn server.asgi:application -k server.asgi.DjangoUvicornWorker -w 4 --host 0.0.0.0 --port 8000

