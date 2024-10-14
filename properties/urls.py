from django.urls import path
from .views import CreatePropertyView


urlpatterns = [
	path('properties/add', CreatePropertyView.as_view(), name='create_property')
]
