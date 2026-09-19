import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import collaboration.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kiti.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(collaboration.routing.websocket_urlpatterns)
    ),
})
