"""
WSGI config for fsd_medic project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os

import socketio
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fsd_medic.settings")
application = get_wsgi_application()
from fsd_medic.settings import SOCKET_IO

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
application = socketio.WSGIApp(SOCKET_IO, application)


# from gevent import pywsgi

import eventlet
import eventlet.wsgi

eventlet.wsgi.server(eventlet.listen(("", 8000)), application)
# pywsgi.WSGIServer(('', 8000), application=application).serve_forever()
