from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
import uuid
import enum
import random
from django.utils import timezone

class UserRole(enum.Enum):
	CLIENT = 'client'
	AGENT = 'agent'
	OWNER = 'owner'

class UserManager(BaseUserManager):
	def create_user(self, first_name, last_name, email, role, gender, phone, date_of_birth, location, password=None):
		if not email:
			raise ValueError("Email field must be set")
		if not first_name:
			raise ValueError("First name field must be set")
		if not last_name:
			raise ValueError("Last name field must be set")
		if not gender:
			raise ValueError("Gender field must be set")
		if not phone:
			raise ValueError('Phone field must be set')
		

		email = self.normalize_email(email)
		user = self.model(email=email, first_name=first_name, last_name=last_name, gender=gender, phone=phone, role=role, date_of_birth=date_of_birth, location=location)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, first_name, last_name, email, gender, phone, password=None):
		user = self.create_user(email=email, first_name=first_name, last_name=last_name, gender=gender, phone=phone, password=password)
		user.is_admin = True
		user.is_staff = True
		user.save(using=self._db)
		return user
	

class User(AbstractBaseUser):

	GENDER_CHOICES = (('male', 'Male'), ('female', 'Female'))

	user_id = models.UUIDField(default=uuid.uuid4, primary_key=True)
	first_name = models.CharField(max_length=255)
	last_name = models.CharField(max_length=255)
	email = models.CharField(max_length=255, unique=True)
	date_of_birth = models.DateField()
	gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default='male')
	phone = models.CharField(max_length=255)
	apartment_type = models.CharField(max_length=255)
	location = models.CharField(max_length=255)
	latitude = models.FloatField(null=True, blank=True)
	longitude = models.FloatField(null=True, blank=True)
	role = models.CharField(max_length=10, choices=[(role.name, role.value) for role in UserRole], default=UserRole.CLIENT.value)
	created_at = models.DateTimeField(auto_now_add=True)
	is_active = models.BooleanField(default=True)
	is_verified = models.BooleanField(default=False)

	is_admin = models.BooleanField(default=False)
	is_staff = models.BooleanField(default=False)

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['first_name', 'last_name', 'phone', 'date_of_birth']

	objects = UserManager()

	def __str__(self):
		return self.first_name
	
	@property
	def is_superuser(self):
		return self.is_admin
	
	def has_perm(self, perm, obj=None):
		return self.is_admin
	
	def has_module_perms(self, app_label):
		return self.is_admin
	


class OTP(models.Model):
	email = models.EmailField()
	otp = models.CharField(max_length=6)
	is_verified = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	expires_at = models.DateTimeField()

	def is_expired(self):
		return timezone.now() > self.expires_at
	

class Client(models.Model):
	GENDER_CHOICES = (('male', 'Male'), ('female', 'Female'))

	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile', primary_key=True)
	partner = models.BooleanField(default=False)
	partner_age = models.IntegerField(default=0)
	partner_gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default='male')

	def __str__(self):
		return f"Client: {self.user.first_name}"


class Agent(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agent_profile', primary_key=True)
	is_verified = models.BooleanField(default=False)

	def __str__(self):
		return f"Agent {self.user.first_name}"


class Owner(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='owner_profile', primary_key=True)

	def __str__(self):
		return f"Owner {self.user.first_name}"