from django.urls import path
from .views import CreatePropertyView, PropertyListView


urlpatterns = [
	path('properties/add', CreatePropertyView.as_view(), name='create_property'),
	path('properties', PropertyListView.as_view(), name='property_list'),
]
