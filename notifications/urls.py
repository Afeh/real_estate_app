from django.urls import path
from .views import GetNotificationPreferences, SubscribeToNotifications, UnsubscribefromNotifications

urlpatterns = [
	path('notifications/subscribe', SubscribeToNotifications.as_view(), name='subscribe'),
	path('notifications/preferences', GetNotificationPreferences.as_view(), name='get_preferences'),
	path('notifications/unsubscribe', UnsubscribefromNotifications.as_view(), name='unsubscribe')
]