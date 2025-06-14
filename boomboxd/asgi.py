"""
ASGI config for halfnote project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'boomboxd.settings')

application = get_asgi_application() 