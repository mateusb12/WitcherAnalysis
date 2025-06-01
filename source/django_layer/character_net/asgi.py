import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

# Correct the import path for routing
from django_layer.api import routing as api_routing

# Correct the settings module path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_layer.character_net.settings')

application = ProtocolTypeRouter({
  "http": get_asgi_application(),
  "websocket": AuthMiddlewareStack(
        URLRouter(
            api_routing.websocket_urlpatterns
        )
    ),
})

