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
		

