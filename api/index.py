import os
import sys

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'boomboxd.settings')

# Import Django and configure it
import django
django.setup()

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application

# Vercel expects the WSGI app to be named 'app'
app = get_wsgi_application()

 