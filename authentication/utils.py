import random
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from .models import OTP

def generate_otp(email):
	# otp_code = str(random.randint(100000, 999999))
	otp_code = "123456"
	expiry_time = timezone.now() + timedelta(minutes=10)

	OTP.objects.create(email=email, otp=otp_code, expires_at=expiry_time)

	send_mail(
		subject="OTP Code from Real Estate Team",
		message=f'Your OTP code is {otp_code}. Please do not share with anybody. Your code is valid for 10 minutes.',
		from_email='realestate@example.com',
		recipient_list=[email],
	)