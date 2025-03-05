from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db import connections
from django.db.utils import OperationalError
from django.core.cache import cache
import redis

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    # Check database
    try:
        connections['default'].cursor()
        db_status = "healthy"
    except OperationalError:
        db_status = "unhealthy"

    # Check Redis
    try:
        cache.set('health_check', 'ok', timeout=1)
        cache_status = "healthy" if cache.get('health_check') == 'ok' else "unhealthy"
    except redis.ConnectionError:
        cache_status = "unhealthy"

    return Response({
        'status': 'healthy' if db_status == "healthy" and cache_status == "healthy" else "unhealthy",
        'database': db_status,
        'cache': cache_status
    }) 