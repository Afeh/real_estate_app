from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import PropertySerializer
from authentication.models import Agent, Owner


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
