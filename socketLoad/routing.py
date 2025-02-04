# your_app_name/routing.py

from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/switch-control/', consumers.MyWebSocketConsumer.as_asgi()),  # WebSocket path for switch control
    path('ws/current-values/', consumers.CurrentValuesConsumer.as_asgi()),  # WebSocket path for current values
]
