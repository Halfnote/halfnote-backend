"""
Halfnote Middleware
Simple username redirect middleware for maintaining user profile URLs
"""

from django.http import HttpResponsePermanentRedirect
import re


class UsernameRedirectMiddleware:
    """Simple middleware for username redirects"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Add any username redirects here if needed
        self.username_redirects = {
            # 'old_username': 'new_username',
        }
    
    def __call__(self, request):
        # Check for username redirects in API URLs
        if self.username_redirects:
            path = request.path
            user_pattern = re.match(r'^(/api/accounts)?/users/([^/]+)(/.*)?$', path)
            
            if user_pattern:
                api_prefix = user_pattern.group(1) or ''
                username = user_pattern.group(2)
                suffix = user_pattern.group(3) or ''
                
                if username.lower() in self.username_redirects:
                    target_username = self.username_redirects[username.lower()]
                    new_path = f"{api_prefix}/users/{target_username}{suffix}"
                    
                    if request.GET:
                        new_path += '?' + request.GET.urlencode()
                    
                    return HttpResponsePermanentRedirect(new_path)
        
        return self.get_response(request)