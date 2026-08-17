#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing uv..."
pip install uv

echo "Installing dependencies..."
uv sync --frozen --no-dev

echo "Running migrations..."
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Build process completed successfully!"
