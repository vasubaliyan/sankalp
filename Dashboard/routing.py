# Dashboard/routing.py
from django.urls import re_path
from . import consumers  # this will import Dashboard/consumers.py

websocket_urlpatterns = [
    re_path(r"ws/dashboard/$", consumers.DashboardConsumer.as_asgi()),
]
