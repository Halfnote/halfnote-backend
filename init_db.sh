#!/bin/bash

# Exit on error
set -e

echo "Creating initial migrations..."
python manage.py makemigrations accounts
python manage.py makemigrations music
python manage.py makemigrations reviews

echo "Applying migrations..."
python manage.py migrate

echo "Creating static files..."
python manage.py collectstatic --noinput

echo "Database initialization complete!" 