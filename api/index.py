import os
import sys
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'boomboxd.settings')

# Import Django WSGI application
import django
django.setup()

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Vercel handler
def handler(request, response):
    return application(request, response) 