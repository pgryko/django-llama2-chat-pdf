#!/bin/sh

# Wait for database to get available
./wait-for-it.sh db:5432 --timeout=30

# Run migrations
python manage.py migrate --noinput

# Start server
uvicorn server.asgi:application --reload  --reload-include "*.html" --host 0.0.0.0 --port 8000
