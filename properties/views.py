from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import PropertySerializer
from authentication.models import Agent, Owner
from django.db.models import Q
from .models import Property
from math import radians, sin, cos, sqrt, atan2


class CreatePropertyView(APIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication]

	def post(self, request):
		user = request.user

		if (user.is_verified and user.is_active):
			if (hasattr(user, 'agent_profile') or hasattr(user, 'owner_profile') or user.is_admin):
				serializer = PropertySerializer(data=request.data)

				if serializer.is_valid():
					agent_id = serializer.validated_data['agent_id']
					owner_id = serializer.validated_data['owner_id']
					try:
						agent_instance = Agent.objects.get(pk=agent_id)
						owner = Owner.objects.get(pk=owner_id)
					
						if hasattr(user, 'agent_profile'):
							agent = user.agent_profile
						else:
							agent = agent_instance

						property_instance = serializer.save(agent=agent, owner=owner)

						data = {
							'status': 'success',
							'message': 'Property was successfully created',
							'data': {
								'property': PropertySerializer(property_instance).data
							}
						}
						return Response(data, status=status.HTTP_201_CREATED)
					except Agent.DoesNotExist or Owner.DoesNotExist:
						return Response({
							'status': 'error',
							'message': 'Agent or Owner does not exist. Invalid agent_id or owner_id'
						}, status=status.HTTP_400_BAD_REQUEST)
				else:
					errors = serializer.errors
					return Response(errors, status=status.HTTP_400_BAD_REQUEST)
			else:
				return Response({
					'status': 'error',
					'message': 'You are not authorized to create a property'
				}, status=status.HTTP_403_FORBIDDEN)
		elif (user.is_verified == False):
				return Response({
						'status': 'error',
						'message': 'User is not verified'
					}, status=status.HTTP_400_BAD_REQUEST)

		elif (user.is_active == False):
			return Response({
					'status': 'error',
					'message': 'Account in active'
				}, status=status.HTTP_400_BAD_REQUEST)


class PropertyListView(APIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication]

	def get(self, request):

		user = request.user

		state = request.query_params.get('state')
		city = request.query_params.get('city')
		amenities = request.query_params.get('amenities')
		name = request.query_params.get('name')
		min_price = request.query_params.get('min_price')
		max_price = request.query_params.get('max_price')
		min_bedrooms = request.query_params.get('min_bedrooms')
		max_bedrooms = request.query_params.get('max_bedrooms')
		min_bathrooms = request.query_params.get('min_bathrooms')
		max_bathrooms = request.query_params.get('max_bathrooms')

		# latitude = request.query_params.get('latitude')
		# longitude = request.query_params.get('longitude')

		radius = request.query_params.get('radius', 10)


		queryset = Property.objects.all()

		if state:
			queryset = queryset.filter(state=state)
		if city:
			queryset = queryset.filter(city=city)
		if amenities:
			queryset = queryset.filter(amenities__icontains=amenities)
		if name:
			queryset = queryset.filter(name__icontains=name)
		if min_price:
			queryset = queryset.filter(price__gte=min_price)
		if max_price:
			queryset = queryset.filter(price__lte=max_price)
		if min_bedrooms:
			queryset = queryset.filter(bedroom_number__gte=min_bedrooms)
		if max_bedrooms:
			queryset = queryset.filter(bedroom_number__lte=max_bedrooms)
		if min_bathrooms:
			queryset = queryset.filter(bathroom_number__gte=min_bathrooms)
		if max_bathrooms:
			queryset = queryset.filter(bathroom_number__lte=max_bathrooms)

		if (user.latitude and user.longitude):
			user_latitude = float(user.latitude)
			user_longtitude = float(user.longitude)

			queryset = [prop for prop in queryset if self.is_within_radius(user_latitude, user_longtitude, prop.latitude, prop.longitude, float(radius))]


		if not queryset:
			return Response({
				'status': 'Not Found',
				'message': 'No properties found matching your search'
			}, status=status.HTTP_404_NOT_FOUND)

		serializer = PropertySerializer(queryset, many=True)

		return Response({
			'status': 'success',
			'message': 'Properties retrieved successfully',
			'properties': serializer.data
		}, status=status.HTTP_200_OK)
	
	
	def is_within_radius(self, user_lat, user_lon, prop_lat, prop_lon, radius_km):
		#Haversine Function

		R = 6371.0

		user_lat_rad = radians(user_lat)
		user_lon_rad = radians(user_lon)
		prop_lat_rad = radians(prop_lat)
		prop_lon_rad = radians(prop_lon)


		dlat = prop_lat_rad - user_lat_rad
		dlon = prop_lon_rad - user_lon_rad

		a = sin(dlat/2)**2 + cos(user_lat_rad) * cos(prop_lat_rad) * sin(dlon/2)**2
		c = 2 * atan2(sqrt(a), sqrt(1-a))

		distance = R * c

		return distance <= radius_km


class 