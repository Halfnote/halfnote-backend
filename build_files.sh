#!/bin/bash
# Build script for Vercel deployment

# Install Python dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput 