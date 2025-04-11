import logging
from django.conf import settings
from django.http import JsonResponse
from rest_framework import status

logger = logging.getLogger(__name__)

class ErrorHandlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        logger.error(f"Unhandled exception: {str(exception)}", exc_info=True)
        
        return JsonResponse({
            'status': 'error',
            'detail': str(exception) if settings.DEBUG else 'Please try again later'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 