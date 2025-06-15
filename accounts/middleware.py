from django.http import HttpResponsePermanentRedirect
from django.urls import resolve, reverse
from django.conf import settings
import re

class UsernameRedirectMiddleware:
    """
    Middleware to handle username redirects (e.g., /users/vivek -> /users/viv360)
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Define username redirects
        self.username_redirects = {
            'vivek': 'viv360',
            # Add more redirects here as needed
        }
    
    def __call__(self, request):
        # Check if this is a user profile URL that needs redirecting
        path = request.path
        
        # Match patterns like /users/username/ or /api/accounts/users/username/
        user_pattern = re.match(r'^(/api/accounts)?/users/([^/]+)(/.*)?$', path)
        
        if user_pattern:
            api_prefix = user_pattern.group(1) or ''  # '/api/accounts' or ''
            username = user_pattern.group(2)
            suffix = user_pattern.group(3) or ''  # '/reviews/', '/followers/', etc.
            
            # Check if this username should be redirected
            if username.lower() in self.username_redirects:
                target_username = self.username_redirects[username.lower()]
                new_path = f"{api_prefix}/users/{target_username}{suffix}"
                
                # Preserve query parameters
                if request.GET:
                    new_path += '?' + request.GET.urlencode()
                
                return HttpResponsePermanentRedirect(new_path)
        
        response = self.get_response(request)
        return response 