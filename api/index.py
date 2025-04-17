from django.core.wsgi import get_wsgi_application
import os

# Set up Django's settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'boomboxd.settings')

# Get the Django WSGI application
application = get_wsgi_application()

# Vercel serverless function handler
def handler(request):
    """
    Vercel serverless function handler to process requests
    """
    return application(request) 