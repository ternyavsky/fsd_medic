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

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fsd_medic.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()

from social import routing

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': URLRouter(
        routing.websocket_urlpatterns
    )

})
