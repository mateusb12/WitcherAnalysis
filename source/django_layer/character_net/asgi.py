"""
ASGI config for django_books project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.sessions import SessionMiddlewareStack
from django.core.asgi import get_asgi_application

import django_layer
from django_layer.api import routing

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_layer.settings')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_layer.character_net.settings')

# application = get_asgi_application()

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": SessionMiddlewareStack( # Wrap URLRouter
        URLRouter(
            routing.websocket_urlpatterns
        )
    ),
})

import django_layer.character_net.urls