from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import NotificationPreferenceSerializer
from .models import NotificationPreference


class SubscribeToNotifications(APIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication]

	def post(self, request):

		user = request.user

		if (user.is_verified and user.is_active):

			serializer = NotificationPreferenceSerializer(data=request.data, context={'request', request})

			if serializer.is_valid():
				serializer.save(user=request.user)

				return Response({
					'status': 'success',
					'message': 'Subscribed to notifications successfully'
				}, status=status.HTTP_201_CREATED)
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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


class GetNotificationPreferences(APIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication]

	def get(self, request):

		user = request.user

		if (user.is_verified and user.is_active):
			preferences = NotificationPreference.objects.filter(user=request.user)
			if preferences:
				serializer = NotificationPreferenceSerializer(preferences, many=True)
				return Response({
					'status': 'success',
					'message': 'user preferences retrieved successfully',
					'preferences': serializer.data
				}, status=status.HTTP_200_OK)
			return Response({
				'status': 'error',
				'message': 'No preferences found for this user'
			})

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


class UnsubscribefromNotifications(APIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication]

	def delete(self, request):

		user = request.user

		if (user.is_verified and user.is_active):
			NotificationPreference.objects.filter(user=request.user).delete()
			return Response({
				'status': 'success',
				'message': 'you have unsuscribed from notifications'
			}, status=status.HTTP_200_OK)

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