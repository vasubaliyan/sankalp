"""
ASGI config for Sankalp project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

# import os

# from django.core.asgi import get_asgi_application

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Sankalp.settings")

# application = get_asgi_application()


"""
ASGI config for Sankalp project with WebSocket (Channels) support.
"""

# Sankalp/asgi.py
import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import Dashboard.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Sankalp.settings")
django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(Dashboard.routing.websocket_urlpatterns)
    ),
})


