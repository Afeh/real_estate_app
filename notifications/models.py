from django.db import models
from authentication.models import User

class NotificationPreference(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	city = models.CharField(max_length=255)
	price_min = models.IntegerField(null=True, blank=True)
	price_max = models.IntegerField(null=True, blank=True)
	max_bedroom = models.IntegerField(null=True, blank=True)
	min_bedroom = models.IntegerField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	# property_type = models.IntegerField(null=True, blank=True)


