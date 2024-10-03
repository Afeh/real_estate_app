from rest_framework import status
from rest_framework.views import APIView
from .serializers import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from django.contrib.auth import get_user_model, authenticate, login

User = get_user_model


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




