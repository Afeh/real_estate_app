from rest_framework import status
from rest_framework.views import APIView
from .models import Client, Agent, Owner
from .serializers import UserSerializer, ForgotPasswordViewSerializer, SetNewPasswordViewSerializer, UpdateProfileSerializer, ClientProfileUpdateSerializer, AgentProfileUpdateSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model, authenticate, login
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse
from django.shortcuts import get_object_or_404
from .models import OTP
from .utils import generate_otp
from uuid import UUID
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
	

class ForgotPasswordView(APIView):
	def post(self, request):
		serializer = ForgotPasswordViewSerializer(data=request.data)
		if serializer.is_valid():
			email = serializer.validated_data['email']

			try: 
				user = User.objects.get(email=email)
			except User.DoesNotExist:
				return Response({'error': 'User with this email does not exist'}, status=status.HTTP_400_BAD_REQUEST)
			
			token = default_token_generator.make_token(user)
			uid = urlsafe_base64_encode(force_bytes(user.pk))

			reset_link = request.build_absolute_uri(
				reverse('password-reset', kwargs={'uidb64': uid, 'token': token})
			)

			subject = "Password Reset Request"
			send_mail(
				subject = "Password Reset Request from Real Estate Team",
				message=f'Click the link below to reset your password: {reset_link}',
				from_email='realestate@example.com',
				recipient_list=[email],
			)
			return Response({'message': 'Password reset link sent'}, status=status.HTTP_200_OK)
		
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	

class PasswordResetView(APIView):
	def post(self, request, uidb64, token):
		try:
			uid = force_str(urlsafe_base64_decode(uidb64))
			user = User.objects.get(pk=uid)
		except (User.DoesNotExist):
			return Response({'error': 'Invalid token or user ID'}, status=status.HTTP_400_BAD_REQUEST)

		# To check if the token is valid
		if not default_token_generator.check_token(user, token):
			return Response({'error': 'Invalid/expired token'}, status=status.HTTP_400_BAD_REQUEST)
		
		serializer = SetNewPasswordViewSerializer(data=request.data)
		if serializer.is_valid():
			new_password = serializer.validated_data['new_password']
			user.set_password(new_password)
			user.save()
			return Response({'message': 'Password reset successful!'}, status=status.HTTP_200_OK)
		
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetClientDetail(APIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication]

	def get(self, request, client_id):
		try:
			client = Client.objects.get(user__user_id=client_id)
			data = {
				"status": "success",
				"message": "Client Details Retrieved Successfully",
				"data" : {
					'first_name': client.user.first_name,
					'last_name': client.user.last_name,
					'email': client.user.email,
					'phone': client.user.phone,
					'date_of_birth': client.user.date_of_birth,
					'role': client.user.role
				}
			}
			return Response(data, status=status.HTTP_200_OK)
		except (Client.DoesNotExist):
			return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)


class GetAgentDetail(APIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication]

	def get(self, request, agent_id):
		try:
			agent = Agent.objects.get(user__user_id=agent_id)
			data = {
				"status": "success",
				"message": "Agent Details Retrieved Successfully",
				"data" : {
					'first_name': agent.user.first_name,
					'last_name': agent.user.last_name,
					'email': agent.user.email,
					'phone': agent.user.phone,
					'is_verified': agent.is_verified,
					'role': agent.user.role
				}
			}
			return Response(data, status=status.HTTP_200_OK)
		except (Agent.DoesNotExist):
			return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)


class UpdateUserProfile(APIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication]

	def patch(self, request, user_id):
		try:
			user = User.objects.get(user_id=user_id)

			user_serializer = UpdateProfileSerializer(user, data=request.data, partial=True)
			if user_serializer.is_valid():
				user_serializer.save()
			else:
				return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
			
			if hasattr(user, 'client_profile'):
				client = user.client_profile
				client_serializer = ClientProfileUpdateSerializer(client, data=request.data, partial=True)
				if client_serializer.is_valid():
					client_serializer.save()
					data = {
						"status": "success",
						"message": "Client Details Updated Successfully",
						"data" : {
							'first_name': client.user.first_name,
							'last_name': client.user.last_name,
							'email': client.user.email,
							'phone': client.user.phone,
							'date_of_birth': client.user.date_of_birth,
							'partner': client.partner,
							'partner_age': client.partner_age,
							'partner_gender': client.partner_gender
						}
					}
				else:
					return Response(client_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

			elif hasattr(user, 'agent_profile'):
				agent = user.agent_profile

				if 'is_verified' in request.data:
					if not request.user.is_admin:
						return Response({
							'status': 'Bad Request',
							'message': 'You do not have permission to change verification status'
							}, status=status.HTTP_403_FORBIDDEN
						)
					
				agent_serializer = AgentProfileUpdateSerializer(agent, data=request.data, partial=True)
				if agent_serializer.is_valid():
					agent_serializer.save()
					data = {
						"status": "success",
						"message": "Agent Details Updated Successfully",
						"data" : {
							'first_name': agent.user.first_name,
							'last_name': agent.user.last_name,
							'email': agent.user.email,
							'phone': agent.user.phone,
							'is_verified': agent.is_verified
						}
					}
				else:
					return Response(agent_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

			return Response(data, status=status.HTTP_201_CREATED)
		
		except User.DoesNotExist:
			return Response({
				'status': 'Bad Request',
				'message': 'Error. User does not exist'
			}, status=status.HTTP_404_NOT_FOUND)


class DeleteUserProfile(APIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication]

	def delete(self, request, user_id):

		user = request.user
		if (user.user_id == user_id):
			try:
				user = User.objects.get(user_id=user_id)
				user.delete()
				return Response({
					"status": "success",
					"message": "User Profile Deleted Successfully"
				}, status=status.HTTP_200_OK)
			except User.DoesNotExist:
				return Response({
					"status": "error",
					"message": "User not found"
				}, status=status.HTTP_404_NOT_FOUND)
		else:
			return Response({
				"status": "error",
				"message": "You do not have permission to delete this user"
			}, status=status.HTTP_403_FORBIDDEN)