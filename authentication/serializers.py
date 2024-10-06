from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
	password = serializers.CharField(write_only=True)
	confirm_password = serializers.CharField(write_only=True)

	class Meta:
		model = User
		fields = ['first_name', 'last_name', 'email', 'phone', 'gender', 'role', 'date_of_birth', 'location','password', 'confirm_password']

	def validate(self, data):
		if data['password'] != data['confirm_password']:
			raise serializers.ValidationError("Passwords do not match.")
		if User.objects.filter(email=data['email']).exists():
			raise serializers.ValidationError("Email already exsists.")
		return data
	
	def create(self, validated_data):
		validated_data.pop('confirm_password')
		user = User.objects.create_user(**validated_data)
		return user
	

class ForgotPasswordViewSerializer(serializers.Serializer):
	email = serializers.EmailField()

class SetNewPasswordViewSerializer(serializers.Serializer):
	new_password = serializers.CharField(min_length=8, write_only=True)
	confirm_password = serializers.CharField(min_length=8, write_only=True)

	def validate(self, data):
		if data['new_password'] != data['confirm_password']:
			raise serializers.ValidationError("Passwords do not match.")
		return data
