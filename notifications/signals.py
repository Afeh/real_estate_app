from django.db.models.signals import post_save
from django.dispatch import receiver
from properties.models import Property
from .models import NotificationPreference
from django.core.mail import send_mail


@receiver(post_save, sender=Property)
def notify_users_on_new_property(sender, instance, created, **kwargs):
	if created:
		matching_preferences = NotificationPreference.objects.filter(
			city__icontains = instance.city,
			price_min__gte = instance.price,
			price_max__lte = instance.price,
			max_bedroom__lte = instance.bedroom_number,
			min_bedroom__gte = instance.bedroom_number
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

	send_mail(subject=subject, message=message, from_email='realestate@example.com', recipient_list=[user.email])
	