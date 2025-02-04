import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.layers import get_channel_layer
from socketLoad.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jarvisBackend.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # Handles HTTP requests
    "websocket": URLRouter(  # Directly route WebSocket connections
        websocket_urlpatterns
    ),
})

# Ensure Redis is properly configured as the channel layer
channel_layer = get_channel_layer()


# application = ProtocolTypeRouter({
#     "http": django_asgi_app,  # Handles HTTP requests
#     "websocket": AuthMiddlewareStack(  # Handles WebSocket requests with authentication
#         URLRouter(websocket_urlpatterns)
#     ),
# })
