#!/bin/bash
# Build script for Vercel deployment

echo "Building the project..."
pip install -r requirements.txt

echo "Make DB migrations..."
python manage.py makemigrations
python manage.py makemigrations music
python manage.py makemigrations reviews
python manage.py makemigrations accounts

echo "Apply DB migrations..."
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Build completed successfully!" 