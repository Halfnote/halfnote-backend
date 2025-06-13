import os
import sys
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Set environment variables
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'boomboxd.settings')
os.environ.setdefault('DEBUG', 'False')

try:
    # Import Django WSGI application
    import django
    django.setup()
    
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    
    # Export for Vercel
    app = application
    
except Exception as e:
    print(f"Error setting up Django: {e}")
    
    # Fallback handler
    def app(environ, start_response):
        status = '500 Internal Server Error'
        headers = [('Content-type', 'text/plain')]
        start_response(status, headers)
        return [f'Django setup error: {str(e)}'.encode()]

# Vercel handler
def handler(request, response):
    return app(request, response) 