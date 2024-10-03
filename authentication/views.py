from rest_framework import status
from rest_framework.views import APIView
from .serializers import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from django.contrib.auth import get_user_model, authenticate, login
from .models import OTP
from .utils import generate_otp
import random


User = get_user_model()


class RegisterView(APIView):
	def post(self, request):
		serializer = UserSerializer(data=request.data)

		if serializer.is_valid():
			user = serializer.save()
			refresh = RefreshToken.for_user(user)
			data = {
				"status": "success",
				"message": "Registration Successful",
				"data" : {
					"access_token": str(refresh.access_token),
					"user": UserSerializer(user).data
				}
			}
			return Response(data, status=status.HTTP_201_CREATED)
		else:
			errors = serializer.errors
			return Response(errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class LoginView(APIView):
	def post(self, request):
		email = request.data.get('email')
		password = request.data.get('password')

		user = authenticate(request, username=email, password=password)
		if user:
			refresh_token = RefreshToken.for_user(user)
			login(request, user)

			data = {
				"status": "success",
				"message": "Login Successful",
				"data": {
					"access_token": str(refresh_token.access_token),
					"user": UserSerializer(user).data
				}
			}
			return Response(data, status=status.HTTP_200_OK)
		else:
			data = {
				"status": "Bad Request",
				"message": "Authentication failed",
				"status_code": 401
			}
			return Response(data, status=status.HTTP_401_UNAUTHORIZED)
		

class SendOTPView(APIView):
	def post(self, request):
		email = request.data.get('email')

		if not email:
			return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
		
		if not User.objects.filter(email=email).exists():
			return Response({"message": "Email does not exist"}, status=status.HTTP_400_BAD_REQUEST)
		
		generate_otp(email)
		return Response({"message": "OTP sent to your email"}, status=status.HTTP_200_OK)


class VerifyOTPView(APIView):
	def post(self, request):
		email = request.data.get('email')
		otp_code = request.data.get('otp')

		try:
			otp = OTP.objects.filter(email=email, otp=otp_code).latest('created_at')

			if otp.is_verified:
				return Response({"message": "OTP has already been used"}, status=status.HTTP_400_BAD_REQUEST)
		
			if otp.is_expired():
				return Response({"message":"OTP has expired"}, status=status.HTTP_400_BAD_REQUEST)
			
			otp.is_verified = True
			otp.save()
			return Response({"message": "OTP verified successfully"}, status=status.HTTP_200_OK)
		
		except OTP.DoesNotExist:
			return Response({"message": "Invalid OTP or email"}, status=status.HTTP_400_BAD_REQUEST)
		


class ResendOTPView(APIView):
	def post(self, request):
		email = request.data.get('email')

		if not User.objects.filter(email=email).exists():
			return Response({"message": "Email does not exist"}, status=status.HTTP_400_BAD_REQUEST)
		
		generate_otp(email)
		return Response({"message": "OTP has been resent to your mail"}, status=status.HTTP_200_OK)