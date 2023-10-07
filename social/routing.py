from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<chat_uuid>[0-9a-f-]+)/(?P<user_id>\w+)/$", consumers.MyConsumer.as_asgi()),
    re_path(r"ws/notify/(?P<user_id>\w+)/$", consumers.NotifyConsumer.as_asgi())

]
