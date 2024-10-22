from rest_framework import serializers
from .models import NotificationPreference


class NotificationPreferenceSerializer(serializers.ModelSerializer):

	class Meta:
		model = NotificationPreference
		fields =['city', 'price_min', 'price_max', 'max_bedroom', 'min_bedroom']