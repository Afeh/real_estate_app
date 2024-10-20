from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import PropertySerializer, EditPropertySerializer, CreatePropertyReviewSerializer
from authentication.models import Agent, Owner
from .models import Property, PropertyReviews
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
					'message': 'Account inactive'
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
		availability = request.query_params.get('availability')
		rating = request.query_params.get('rating')

		# latitude = request.query_params.get('latitude')
		# longitude = request.query_params.get('longitude')

		radius = request.query_params.get('radius', 10)


		queryset = Property.objects.all()

		if state:
			queryset = queryset.filter(state__icontains=state)
		if city:
			queryset = queryset.filter(city__icontains=city)
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
		if rating:
			queryset = queryset.filter(average_rating__gte=rating)
		if availability:
			is_available = availability.lower() == 'true'
			queryset = queryset.filter(is_available=is_available)

		if (user.latitude and user.longitude):
			user_latitude = float(user.latitude)
			user_longitude = float(user.longitude)

			queryset = [prop for prop in queryset if self.is_within_radius(user_latitude, user_longitude, prop.latitude, prop.longitude, float(radius))]


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



class GetPropertyView(APIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication]

	def get(self, request, id):
		try:
			property_object = Property.objects.get(property_id=id)
			reviews = PropertyReviews.objects.filter(property=property_object)

			data = {
				'status': 'success',
				'message': 'Property retrieved',
				'data': {
					'property': PropertySerializer(property_object).data,
					'reviews': CreatePropertyReviewSerializer(reviews, many=True).data
				}
			}
			return Response(data, status=status.HTTP_200_OK)
		except Property.DoesNotExist:
			return Response({
				'status': 'error',
				'message': 'Property not found'
			}, status=status.HTTP_404_NOT_FOUND)



class DeletePropertyView(APIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication]

	def delete(self, request, id):
		if (request.user.is_admin):
			try:
				property_object = Property.objects.get(pk=id)
				property_object.delete()
				return Response({
					'status': 'success',
					'message': 'Property was deleted successfully'
				}, status=status.HTTP_200_OK)
			except Property.DoesNotExist:
				return Response({
					'status': 'error',
					'message': 'Property with that id does not exist'
				}, status=status.HTTP_404_NOT_FOUND)
		else:
			return Response({
				'status': 'error',
				'message': 'You do not have the permission to delete a property'
			}, status = status.HTTP_403_FORBIDDEN)


class EditPropertyView(APIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication]

	def patch(self, request, id):

		if (request.user.is_verified and request.user.is_active):
			try:
				property_object = Property.objects.get(pk=id)

				if ((((property_object.agent.pk == request.user.user_id) and property_object.agent.is_verified) or (property_object.owner.pk == request.user.user_id)) or request.user.is_admin):
			
					if 'is_verified' in request.data:
						if not request.user.is_admin:
							return Response({
								'status': 'Bad request',
								'message': 'You do not have the permission to change property verification status'
							}, status=status.HTTP_403_FORBIDDEN)

					property_serializer = EditPropertySerializer(property_object, data=request.data, partial=True)
		
					if property_serializer.is_valid():
						property_serializer.save()

						data = {
							'status': 'success',
							'message': 'Property Edited and Saved successfully',
							'data': {
								'property': PropertySerializer(property_object).data
							}
						}
						return Response(data, status=status.HTTP_200_OK)

					else:
						return Response(property_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

				else:
					return Response({
						'status': 'error',
						'message': 'User not authorized to make changes to Property'
					}, status=status.HTTP_403_FORBIDDEN)

			except Property.DoesNotExist:
				return Response({
					'status': 'Bad Request',
					'message': 'Error, Property does not exist'
				}, status=status.HTTP_404_NOT_FOUND)

		elif (request.user.is_verified == False):
			return Response({'status': 'error',
						'message': 'User is not verified'}, status=status.HTTP_400_BAD_REQUEST)

		elif (request.user.is_active == False):
			return Response({'status': 'error',
							'message': 'Account inactive'}, status=status.HTTP_400_BAD_REQUEST)


class CreatePropertyReview(APIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication]

	def post(self, request):
		user = request.user

		if (user.is_verified and user.is_active):
			if hasattr(user, 'client_profile'):

				client = user.client_profile
	
				serializer = CreatePropertyReviewSerializer(data=request.data)

				if serializer.is_valid():
					property_id = serializer.validated_data['property_id']

					try:
						property_instance = Property.objects.get(pk=property_id)

						property_serializer = serializer.save(property=property_instance, created_by=client)

						data = {
							'status': 'success',
							'message': 'Property review sucessfully dropped',
							'data' : {
								'review': CreatePropertyReviewSerializer(property_serializer).data
							}
						}
						return Response(data, status=status.HTTP_201_CREATED)

					except Property.DoesNotExist:
						return Response({
							'status': 'error',
							'message': 'Property not found'
						}, status=status.HTTP_404_NOT_FOUND)
				else:
					return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

			else:
				return Response({
					'status': 'Forbidden',
					'message': 'Only clients can drop property reviews'
				}, status=status.HTTP_403_FORBIDDEN)

		elif (request.user.is_verified == False):
			return Response({'status': 'error',
						'message': 'User is not verified'}, status=status.HTTP_400_BAD_REQUEST)

		elif (request.user.is_active == False):
			return Response({'status': 'error',
							'message': 'Account inactive'}, status=status.HTTP_400_BAD_REQUEST)