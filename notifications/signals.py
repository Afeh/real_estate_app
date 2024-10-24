from django.db.models.signals import post_save
from django.dispatch import receiver
from properties.models import Property
from .models import NotificationPreference
from django.core.mail import send_mail
from django.db.models import Q


@receiver(post_save, sender=Property)
def notify_users_on_new_property(sender, instance, created, **kwargs):
	if created:

		matching_preferences = NotificationPreference.objects.filter(
			Q(city__icontains=instance.city) |
			Q(price_min__isnull=True) | Q(price_min__lte=instance.price),
			Q(price_max__isnull=True) | Q(price_max__gte=instance.price),
			Q(min_bedroom__isnull=True) | Q(min_bedroom__lte=instance.bedroom_number),
			Q(max_bedroom__isnull=True) | Q(max_bedroom__gte=instance.bedroom_number)
		)


		for preference in matching_preferences:
			user = preference.user
			send_property_notification(user, instance)


def send_property_notification(user, property_instance):
	subject = "New Property Matching Your Preferences!"
	message = f"""
	Hi {user.first_name},

	A new property has been added that matches your preferences!

	Property Name: {property_instance.name},
	City: {property_instance.city},
	State: {property_instance.state},
	Address: {property_instance.address}

	Visit the platform to check it out!
	"""

	send_mail(subject=subject, message=message, from_email='realestateapp.devteam@gmail.com', recipient_list=[user.email], fail_silently=False)
	