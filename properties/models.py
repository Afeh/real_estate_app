from django.db import models
from authentication.models import Agent, Owner
import random
import string


NIGERIAN_STATES = [
	('AB', 'Abia'),
	('AD', 'Adamawa'),
	('AK', 'Akwa Ibom'),
	('AN', 'Anambra'),
	('BA', 'Bauchi'),
	('BY', 'Bayelsa'),
	('BE', 'Benue'),
	('BO', 'Borno'),
	('CR', 'Cross River'),
	('DE', 'Delta'),
	('EB', 'Ebonyi'),
	('ED', 'Edo'),
	('EK', 'Ekiti'),
	('EN', 'Enugu'),
	('GO', 'Gombe'),
	('IM', 'Imo'),
	('JI', 'Jigawa'),
	('KD', 'Kaduna'),
	('KN', 'Kano'),
	('KT', 'Katsina'),
	('KE', 'Kebbi'),
	('KO', 'Kogi'),
	('KW', 'Kwara'),
	('LA', 'Lagos'),
	('NA', 'Nasarawa'),
	('NI', 'Niger'),
	('OG', 'Ogun'),
	('ON', 'Ondo'),
	('OS', 'Osun'),
	('OY', 'Oyo'),
	('PL', 'Plateau'),
	('RV', 'Rivers'),
	('SO', 'Sokoto'),
	('TA', 'Taraba'),
	('YO', 'Yobe'),
	('ZA', 'Zamfara'),
	('FC', 'Federal Capital Territory (Abuja)'),
]


def generate_property_id(state_abbreviation, length=4):
	random_char = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

	return f"{state_abbreviation}-{random_char}"



class Property(models.Model):
	property_id = models.CharField(max_length=10, primary_key=True, unique=True)
	name = models.CharField(max_length=255)
	address = models.TextField()
	state = models.CharField(max_length=2, choices=NIGERIAN_STATES)
	longitude = models.FloatField(null=True, blank=True)
	latitude = models.FloatField(null=True, blank=True)
	is_verified = models.BooleanField(default=False)
	price = models.DecimalField(max_digits=10, decimal_places=2)
	amenities = models.TextField(max_length=255)
	bedroom_number = models.IntegerField()
	bathroom_number = models.IntegerField()
	description = models.TextField()
	agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='property_agent')
	owner = models.ForeignKey(Owner, on_delete=models.CASCADE, null=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def save(self, *args, **kwargs):
		if not self.property_id:
			self.property_id = generate_property_id(self.state)
		super(Property, self).save(*args, **kwargs)


class PropertyImage(models.Model):
	property = models.ForeignKey(Property, on_delete=models.CASCADE)
	image = models.ImageField(upload_to='property_images/', blank=True, null=True)
	caption = models.TextField()

	def __str__(self):
		return f"Image for {self.property.name}"
	

class PropertyVideo(models.Model):
	property = models.ForeignKey(Property, on_delete=models.CASCADE)
	video = models.FileField(upload_to='property_videos/', blank=True, null=True)
	caption = models.TextField()

	def __str__(self):
		return f"Video for {self.property.name}"
	

