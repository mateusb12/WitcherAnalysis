import os
import logging

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

# Correct the import path for routing
from django_layer.api import routing as api_routing

# Correct the settings module path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_layer.character_net.settings')

logger = logging.getLogger("asgi")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            api_routing.websocket_urlpatterns
        )
    ),
})

logger.info("ASGI application initialized with ProtocolTypeRouter.")

# Add logging to track WebSocket connections
def log_websocket_scope(scope):
    logger.info(f"WebSocket connection scope: {scope}")
    return scope

# Wrap the application to log WebSocket scopes
application = log_websocket_scope(application)
