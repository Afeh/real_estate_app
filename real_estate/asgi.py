import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import django
django.setup()
from chat import routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'real_estate.settings')

application = ProtocolTypeRouter({
	"http": get_asgi_application(),
	"websocket": AuthMiddlewareStack(
		URLRouter(
			routing.websocket_urlpatterns
		)
	)
})

app=application