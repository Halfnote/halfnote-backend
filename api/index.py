import os
import sys
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Set environment variables
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'boomboxd.settings')
os.environ.setdefault('DEBUG', 'False')

# Import Django
import django
django.setup()

from django.core.wsgi import get_wsgi_application

# Create the application
app = get_wsgi_application()

 