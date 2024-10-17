from django.db import models
from authentication.models import Agent, Owner, Client
import random
import string

STATES = {
	'Abia': 'AB',
	'Adamawa': 'AD',
	'Akwa Ibom': 'AK',
	'Anambra': 'AN',
	'Bauchi': 'BA',
	'Bayelsa': 'BY',
	'Benue': 'BE',
	'Borno': 'BO',
	'Cross River': 'CR',
	'Delta': 'DE',
	'Ebonyi': 'EB',
	'Edo': 'ED',
	'Ekiti': 'EK',
	'Enugu': 'EN',
	'FCT': 'FC',
	'Gombe': 'GO',
	'Imo': 'IM',
	'Jigawa': 'JI',
	'Kaduna': 'KD',
	'Kano': 'KN',
	'Katsina': 'KT',
	'Kebbi': 'KE',
	'Kogi': 'KO',
	'Kwara': 'KW',
	'Lagos': 'LA',
	'Nasarawa': 'NA',
	'Niger': 'NI',
	'Ogun': 'OG',
	'Ondo': 'ON',
	'Osun': 'OS',
	'Oyo': 'OY',
	'Plateau': 'PL',
	'Rivers': 'RI',
	'Sokoto': 'SO',
	'Taraba': 'TA',
	'Yobe': 'YO',
	'Zamfara': 'ZA'
}

NIGERIAN_STATES = [
	('Abia', 'AB'),
	('Adamawa', 'AD'),
	('Akwa Ibom', 'AK'),
	('Anambra', 'AN'),
	('Bauchi', 'BA'),
	('Bayelsa', 'BY'),
	('Benue', 'BE'),
	('Borno', 'BO'),
	('Cross River', 'CR'),
	('Delta', 'DE'),
	('Ebonyi', 'EB'),
	('Edo', 'ED'),
	('Ekiti', 'EK'),
	('Enugu', 'EN'),
	('Gombe', 'GO'),
	('Imo', 'IM'),
	('Jigawa', 'JI'),
	('Kaduna', 'KD'),
	('Kano', 'KN'),
	('Katsina', 'KT'),
	('Kebbi', 'KE'),
	('Kogi', 'KO'),
	('Kwara', 'KW'),
	('Lagos', 'LA'),
	('Nasarawa', 'NA'),
	('Niger', 'NI'),
	('Ogun', 'OG'),
	('Ondo', 'ON'),
	('Osun', 'OS'),
	('Oyo', 'OY'),
	('Plateau', 'PL'),
	('Rivers', 'RV'),
	('Sokoto', 'SO'),
	('Taraba', 'TA'),
	('Yobe', 'YO'),
	('Zamfara', 'ZA'),
	('Federal Capital Territory', 'FC'),
]



def generate_property_id(state, length=4):
	random_char = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

	return f"{STATES[state]}-{random_char}"



class Property(models.Model):
	property_id = models.CharField(max_length=10, primary_key=True, unique=True)
	name = models.CharField(max_length=255)
	address = models.TextField()
	city = models.CharField(max_length=255)
	state = models.CharField(max_length=50, choices=NIGERIAN_STATES)
	longitude = models.FloatField(null=True, blank=True)
	latitude = models.FloatField(null=True, blank=True)
	is_available = models.BooleanField(default=True)
	is_verified = models.BooleanField(default=False)
	average_rating = models.DecimalField(max_digits=2, decimal_places=1, default=0.0)
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


class PropertyReviews(models.Model):
	property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="reviews")
	created_by = models.ForeignKey(Client, on_delete=models.CASCADE)
	caption = models.TextField()
	rating = models.IntegerField()
	comment = models.TextField()
	is_verified = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)


	def save(self, *args, **kwargs):
		super(PropertyReviews, self).save(*args, **kwargs)
		self.update_property_average_rating()

	def update_property_average_rating(self):
		reviews = PropertyReviews.objects.filter(property=self.property)
		avg_rating = reviews.aggregate(models.Avg('rating'))['rating__avg']
		self.property.average_rating = avg_rating or 0.0
		self.property.save()
