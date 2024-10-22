from rest_framework import serializers
from .models import User, Client, Agent, Owner, Testimonials

NIGERIAN_STATES = {
	'Abia': 'AB',
	'Adamawa': 'AD',
	'Akwa Ibom': 'AK',
	'Anambra': 'AN',
	'Bauchi': 'BA',
	'Bayelsa': 'BY',
	'Benue': 'BE',
	'Borno': 'BO',
	'Cross River': 'CR',
	'Delta': 'DE',
	'Ebonyi': 'EB',
	'Edo': 'ED',
	'Ekiti': 'EK',
	'Enugu': 'EN',
	'FCT': 'FC',
	'Gombe': 'GO',
	'Imo': 'IM',
	'Jigawa': 'JI',
	'Kaduna': 'KD',
	'Kano': 'KN',
	'Katsina': 'KT',
	'Kebbi': 'KE',
	'Kogi': 'KO',
	'Kwara': 'KW',
	'Lagos': 'LA',
	'Nasarawa': 'NA',
	'Niger': 'NI',
	'Ogun': 'OG',
	'Ondo': 'ON',
	'Osun': 'OS',
	'Oyo': 'OY',
	'Plateau': 'PL',
	'Rivers': 'RI',
	'Sokoto': 'SO',
	'Taraba': 'TA',
	'Yobe': 'YO',
	'Zamfara': 'ZA'
}


class UserSerializer(serializers.ModelSerializer):
	password = serializers.CharField(write_only=True)
	confirm_password = serializers.CharField(write_only=True)
	user_id = serializers.UUIDField(read_only=True)

	class Meta:
		model = User
		fields = ['user_id', 'first_name', 'last_name', 'email', 'phone', 'gender', 'role', 'date_of_birth', 'location','password', 'confirm_password']

	def validate(self, data):
		if data['password'] != data['confirm_password']:
			raise serializers.ValidationError("Passwords do not match.")
		if User.objects.filter(email=data['email']).exists():
			raise serializers.ValidationError("Email already exsists.")
		return data
	
	def create(self, validated_data):
		validated_data.pop('confirm_password')
		user = User.objects.create_user(**validated_data)
		if user.role == "CLIENT":
			Client.objects.create(user=user)

		if user.role == "AGENT":
			Agent.objects.create(user=user)

		if user.role == "OWNER":
			Owner.objects.create(user=user)

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


class UpdateProfileSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ['first_name', 'last_name', 'email', 'apartment_type', 'location', 'latitude', 'longitude']

		def update(self, instance, validated_data):
			for attr, value in validated_data.items():
				setattr(instance, attr, value)
			instance.save()
			return instance


class ClientProfileUpdateSerializer(serializers.ModelSerializer):
	class Meta:
		model = Client
		fields = ['partner', 'partner_age', 'partner_gender']


class AgentProfileUpdateSerializer(serializers.ModelSerializer):
	state = serializers.CharField()

	class Meta:
		model = Agent
		fields = ['is_verified', 'state', 'city']

	def validate_state(self, state):
		if state in NIGERIAN_STATES:
			return state
		else:
			raise serializers.ValidationError(f"Invalid state name: {state}")


class CreateAgentTestimonial(serializers.ModelSerializer):

	RATING_CHOICES = [1, 2, 3, 4, 5]

	agent_id = serializers.CharField(write_only=True)
	agent_name = serializers.SerializerMethodField()
	created_by = serializers.SerializerMethodField()
	rating = serializers.IntegerField()
	created_at = serializers.DateTimeField(read_only=True)

	class Meta:
		model = Testimonials
		fields = ['caption', 'testimonial', 'rating', 'created_at', 'created_by', 'agent_name', 'agent_id']

	def get_created_by(self, obj):
		return f"{obj.created_by.user.first_name} {obj.created_by.user.last_name}"
	
	def get_agent_name(self, obj):
		return f"{obj.agent.user.first_name} {obj.agent.user.last_name}"
	
	def validate_rating(self, value):
		if value <= 0:
			raise serializers.ValidationError("Rating must be positive")
		
		if value in self.RATING_CHOICES:
			return value
		else:
			raise serializers.ValidationError("Rating must be between 1 to 5")


class AgentSerializer(serializers.ModelSerializer):

	agent_full_name = serializers.SerializerMethodField()
	phone = serializers.SerializerMethodField()
	email = serializers.SerializerMethodField()


	class Meta:
		model = Agent
		fields = ['agent_full_name', 'phone', 'email', 'state', 'city', 'average_rating', 'is_verified']


	def get_agent_full_name(self, obj):
		return f"{obj.user.first_name} {obj.user.last_name}"
	
	def get_phone(self, obj):
		return f"{obj.user.phone}"
	
	def get_email(self, obj):
		return f"{obj.user.email}"