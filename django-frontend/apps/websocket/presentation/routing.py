from django.urls import re_path

from ..application.consumers import FastAPIProxyConsumer

websocket_urlpatterns = [
    re_path(r"^ws/(?P<path>.*)$", FastAPIProxyConsumer.as_asgi()),
]
