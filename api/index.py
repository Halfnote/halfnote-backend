import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'boomboxd.settings_production')

from boomboxd.wsgi import application

# Create an app variable for Vercel
app = application 