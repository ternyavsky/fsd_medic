from django.urls import re_path, path

from . import consumers

websocket_urlpatterns = [
    path(f"ws/chat/<chat_uuid>/", consumers.MyConsumer.as_asgi()),
    re_path(r"ws/notify/", consumers.NotifyConsumer.as_asgi())

]
