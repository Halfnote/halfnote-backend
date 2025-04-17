from django.core.wsgi import get_wsgi_application

# Set up Django's settings
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'boomboxd.settings')

# Get the Django WSGI application
app = application = get_wsgi_application()

# Function to handle HTTP requests in Vercel
def handler(request, **kwargs):
    """
    This handler is used by Vercel to serve both the Django application
    and static files.
    """
    # Extract path from the request
    path = request.get('path', '')
    
    # Check if the request is for a static file
    if path.startswith('/static/'):
        # Let Django's StaticFilesHandler handle it
        return application(request, **kwargs)
    
    # For all other requests, use the Django application
    return application(request, **kwargs) 