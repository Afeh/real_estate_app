from rest_framework import status
from rest_framework.views import APIView
from .models import Client, Agent, Owner, Testimonials
from .serializers import UserSerializer, ForgotPasswordViewSerializer, SetNewPasswordViewSerializer, UpdateProfileSerializer, ClientProfileUpdateSerializer, AgentProfileUpdateSerializer, CreateAgentTestimonial, AgentSerializer
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
from math import radians, sin, cos, sqrt, atan2
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
				"message": "Authentication failed, Incorrect Password or Email",
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
			user = User.objects.get(email=email)

			if otp.is_verified:
				return Response({"message": "OTP has already been used"}, status=status.HTTP_400_BAD_REQUEST)
		
			if otp.is_expired():
				return Response({"message":"OTP has expired"}, status=status.HTTP_400_BAD_REQUEST)
			
			otp.is_verified = True

			user.is_verified = True

			user.save()
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
				reverse('password_reset', kwargs={'uidb64': uid, 'token': token})
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
			return Response({'error': 'Invalid link'}, status=status.HTTP_400_BAD_REQUEST)

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
		if (request.user.is_verified and request.user.is_active):
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
	
		elif (request.user.is_verified == False):
			return Response({'status': 'error',
						'message': 'User is not verified'}, status=status.HTTP_400_BAD_REQUEST)

		elif (request.user.is_active == False):
			return Response({'status': 'error',
							'message': 'Account in active'}, status=status.HTTP_400_BAD_REQUEST)



class GetAgentDetail(APIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication]

	def get(self, request, agent_id):
		if (request.user.is_verified and request.user.is_active):
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
	
		elif (request.user.is_verified == False):
			return Response({'status': 'error',
							'message': 'User is not verified'}, status=status.HTTP_400_BAD_REQUEST)

		elif (request.user.is_active == False):
			return Response({'status': 'error',
							'message': 'Account in active'}, status=status.HTTP_400_BAD_REQUEST)	


class UpdateUserProfile(APIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication]

	def patch(self, request, user_id):
		if (request.user.is_verified and request.user.is_active):
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
								'average_rating': agent.average_rating,
								'city': agent.city,
								'state': agent.state,
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

		elif (request.user.is_verified == False):
			return Response({'status': 'error',
							'message': 'User is not verified'}, status=status.HTTP_400_BAD_REQUEST)

		elif (request.user.is_active == False):
			return Response({'status': 'error',
							'message': 'Account in active'}, status=status.HTTP_400_BAD_REQUEST)


class DeactivateAccountView(APIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication]

	def patch(self, request, user_id):

		if (request.user.is_verified):
			try:
				user = User.objects.get(user_id = user_id)
				
				if ((str(request.user.user_id) == str(user_id)) or user.is_admin):
					user.is_active = False
					user.save()

					return Response({
						'status': 'success',
						'message': 'User account deactivated successfully'
					}, status=status.HTTP_200_OK)
				else:
					return Response({
						'status': 'Forbidden',
						'message': 'User does not have permission to deactivate account'
					}, status=status.HTTP_403_FORBIDDEN)

			except User.DoesNotExist:
				return Response({
					'status': 'Bad Request',
					'message': 'Error. User does not exist'
				}, status=status.HTTP_404_NOT_FOUND)
		
		else:
			return Response({
					'status': 'error',
					'message': 'User is not verified'
				}, status=status.HTTP_400_BAD_REQUEST)



class ReactivateAccountView(APIView):
	def post(self, request):
		email = request.data.get('email')

		try:
			user = User.objects.get(email=email)
		except User.DoesNotExist:
			return Response({
				'status': 'error',
				'message': 'User with this email does not exist'
			}, status=status.HTTP_404_NOT_FOUND)
		
		token = default_token_generator.make_token(user)
		uid = urlsafe_base64_encode(force_bytes(user.user_id))

		reset_link = request.build_absolute_uri(
			reverse('activate_account', kwargs={'uidb64': uid, 'token': token})
		)

		subject = "Account Reactivation Request"
		send_mail(
			subject="Account Reactivation Request from Real Estate Dev Team",
			message=f'Click the link below to reset your password: \n {reset_link}',
			from_email='realestate@example.com',
			recipient_list= [email]
		)

		return Response({
			'status': 'success',
			'message': 'Reactivation Link Sent to your mail'
		}, status=status.HTTP_200_OK)


class ActivateAccountView(APIView):
	def post(self, request, uidb64, token):
		try:
			uid = force_str(urlsafe_base64_decode(uidb64))
			user = User.objects.get(user_id=uid)
		except (User.DoesNotExist):
			return Response({
				'status': 'error',
				'message':'Invalid link'
			}, status=status.HTTP_400_BAD_REQUEST)
		
		if not default_token_generator.check_token(user, token):
			return Response({
				'status': 'error',
				'message': 'Invalid/Expired token'
			}, status=status.HTTP_400_BAD_REQUEST)
		
		user.is_active = True
		user.save()

		return Response({
			'status': 'success',
			'message': 'Account reactivated successfully'
		}, status=status.HTTP_200_OK)


class SaveUserLocation(APIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication]

	def post(self, request):
		latitude = request.data.get('latitude')
		longitude = request.data.get('longitude')

		if latitude and longitude:
			user = request.user
			user.latitude = latitude
			user.longitude = longitude
			user.save()

			return Response({
				'status': 'success',
				'message': 'Location saved successfully'
			}, status=status.HTTP_200_OK)
		else:
			return Response ({
				'status': 'error',
				'message': 'Latitude and Longitude required'
			}, status=status.HTTP_400_BAD_REQUEST)


class CreateTestimonialView(APIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication]

	def post(self, request):
		user = request.user

		if (user.is_verified and user.is_active):
			if hasattr(user, 'client_profile'):

				client = user.client_profile
	
				serializer = CreateAgentTestimonial(data=request.data)

				if serializer.is_valid():
					agent_id = serializer.validated_data['agent_id']

					try:
						agent_instance = Agent.objects.get(pk=agent_id)

						testimonial_serializer = serializer.save(agent=agent_instance, created_by=client)

						data ={
							'status': 'success',
							'message': 'Testimonial successfully recorded',
							'data': {
								'testimonial': CreateAgentTestimonial(testimonial_serializer).data
							}
						}
						return Response(data, status=status.HTTP_201_CREATED)
				
					except Agent.DoesNotExist:
						return Response({
							'status': 'error',
							'message': 'Agent not found'
						}, status=status.HTTP_404_NOT_FOUND)

			else:
				return Response({
					'status': 'Forbidden',
					'message': 'Only clients can drop Agent Testimonials'
				}, status=status.HTTP_403_FORBIDDEN)

		elif (request.user.is_verified == False):
			return Response({'status': 'error',
						'message': 'User is not verified'}, status=status.HTTP_400_BAD_REQUEST)

		elif (request.user.is_active == False):
			return Response({'status': 'error',
							'message': 'Account inactive'}, status=status.HTTP_400_BAD_REQUEST)


class GetAgentTestimonials(APIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication]

	def get(self, request, agent_id):
		user = request.user

		if (user.is_verified and user.is_active):

	
			try:
				testimonials = Testimonials.objects.filter(agent__pk=agent_id)

				data = {
					'status': 'success',
					'message': 'Testimonials Retrieved',
					'data': {
						'testimonials': CreateAgentTestimonial(testimonials, many=True).data
					}
				}

				return Response(data, status=status.HTTP_200_OK)

			except Testimonials.DoesNotExist or Agent.DoesNotExist:
				return Response({
					'status': 'Not Found',
					'message': 'Testimonials don\'t exist for Agent with inputed agent_id or Invalid agent_id'
				}, status=status.HTTP_404_NOT_FOUND)


		elif (request.user.is_verified == False):
			return Response({'status': 'error',
						'message': 'User is not verified'}, status=status.HTTP_400_BAD_REQUEST)

		elif (request.user.is_active == False):
			return Response({'status': 'error',
							'message': 'Account inactive'}, status=status.HTTP_400_BAD_REQUEST)


class AgentListView(APIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication]

	def get(self, request):

		user = request.user

		city = request.query_params.get('city')
		state = request.query_params.get('state')
		first_name = request.query_params.get('first_name')
		last_name = request.query_params.get('last_name')
		rating = request.query_params.get('rating')

		sort = request.query_params.get('sort', None)

		radius = request.query_params.get('radius', 20)


		queryset = Agent.objects.all()

		if state:
			queryset = queryset.filter(state__icontains=state)
		if city:
			queryset = queryset.filter(city__icontains=city)
		if first_name:
			queryset = queryset.filter(user__first_name__icontains=first_name)
		if last_name:
			queryset = queryset.filter(user__last_name__icontains=last_name)
		if rating:
			queryset = queryset.filter(average_rating__gte=rating)

		if (user.latitude and user.longitude):
			user_latitude = float(user.latitude)
			user_longitude = float(user.longitude)

			queryset = [agent for agent in queryset if agent.user.latitude and agent.user.longitude and self.is_within_radius(user_latitude, user_longitude, agent.user.latitude, agent.user.longitude, float(radius))]
		else:
			pass

		if sort == 'asc':
			queryset = sorted(queryset, key=lambda agent: agent.average_rating)
		elif sort == 'desc':
			queryset = sorted(queryset, key=lambda agent: agent.average_rating, reverse=True)

		if not queryset:
			return Response({
				'status': 'Not found',
				'message': 'No agents found matching your search'
			}, status=status.HTTP_404_NOT_FOUND)
		
		serializer = AgentSerializer(queryset, many=True)

		return Response({
			'status': 'success',
			'message': 'Agents retrieved successfully',
			'agents': serializer.data
		}, status=status.HTTP_200_OK)

	def is_within_radius(self, user_lat, user_lon, agent_lat, agent_lon, radius_km):
		#Haversine Function

		R = 6371.0

		user_lat_rad = radians(user_lat)
		user_lon_rad = radians(user_lon)
		prop_lat_rad = radians(agent_lat)
		prop_lon_rad = radians(agent_lon)


		dlat = prop_lat_rad - user_lat_rad
		dlon = prop_lon_rad - user_lon_rad

		a = sin(dlat/2)**2 + cos(user_lat_rad) * cos(prop_lat_rad) * sin(dlon/2)**2
		c = 2 * atan2(sqrt(a), sqrt(1-a))

		distance = R * c

		return distance <= radius_km
	