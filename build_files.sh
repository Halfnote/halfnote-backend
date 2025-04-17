#!/bin/bash
# Build script for Vercel deployment

echo "Building the project..."
python -m pip install -r requirements.txt

echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Build completed successfully!" 