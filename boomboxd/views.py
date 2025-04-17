from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Simple health check endpoint that returns a 200 OK response.
    """
    return JsonResponse({"status": "ok"})

def welcome(request):
    """
    Simple welcome page for the API.
    """
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Boomboxd API</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
                max-width: 800px;
                margin: 40px auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h1 { color: #2c3e50; margin-top: 0; }
            a { color: #3498db; text-decoration: none; }
            a:hover { text-decoration: underline; }
            ul { padding-left: 20px; }
            li { margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Welcome to Boomboxd API</h1>
            <p>This is the API backend for the Boomboxd application.</p>
            
            <h2>Available Endpoints:</h2>
            <ul>
                <li><a href="/api/albums/">/api/albums/</a> - Browse and search albums</li>
                <li><a href="/api/reviews/">/api/reviews/</a> - View album reviews</li>
                <li><a href="/api/auth/register/">/api/auth/register/</a> - Register a new account</li>
                <li><a href="/api/auth/login/">/api/auth/login/</a> - Login to your account</li>
                <li><a href="/health/">/health/</a> - API health check</li>
            </ul>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html) 