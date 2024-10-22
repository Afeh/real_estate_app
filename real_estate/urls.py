from django.contrib import admin
from django.urls import path, include

urlpatterns = [
	path('admin/', admin.site.urls),
	path('', include('authentication.urls')),
	path('', include('properties.urls')),
	path('', include('notifications.urls')),
]
