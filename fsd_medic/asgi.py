"""
ASGI config for fsd_medic project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

import django
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from social.middleware import JwtAuthMiddlewareStack
import socketio
import eventlet
import eventlet.ws

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fsd_medic.settings')
# os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
# django.setup()

# from social import routing
application = get_asgi_application()
# application = ProtocolTypeRouter({
#     'http': get_asgi_application(),
#     'websocket': JwtAuthMiddlewareStack(URLRouter(
#         routing.websocket_urlpatterns
#     ))

# })
