from django.urls import path
from .views import CreatePropertyView, PropertyListView, GetPropertyView, DeletePropertyView


urlpatterns = [
	path('properties/add', CreatePropertyView.as_view(), name='create_property'),
	path('properties', PropertyListView.as_view(), name='property_list'),
	path('properties/<str:id>', GetPropertyView.as_view(), name='get_property'),
	path('properties/delete/<str:id>', DeletePropertyView.as_view(), name='delete_property')
]
