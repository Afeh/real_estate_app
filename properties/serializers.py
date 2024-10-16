from rest_framework import serializers
from .models import Property

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


class PropertySerializer(serializers.ModelSerializer):

	property_id = serializers.CharField(read_only=True)
	is_available = serializers.BooleanField(read_only=True)
	state = serializers.CharField()
	agent_id = serializers.UUIDField()
	owner_id = serializers.UUIDField()

	agent_full_name = serializers.SerializerMethodField()
	owner_full_name = serializers.SerializerMethodField()

	class Meta:
		model = Property
		fields = ['property_id', 'is_available', 'state', 'city', 'name', 'address', 'longitude', 'latitude', 'price', 'amenities', 'bedroom_number', 'bathroom_number', 'description', 'agent_full_name','agent_id', 'owner_full_name', 'owner_id']

	def get_agent_full_name(self, obj):
		return f"{obj.agent.user.first_name} {obj.agent.user.last_name}"
	
	def get_owner_full_name(self, obj):
		return f"{obj.owner.user.first_name} {obj.owner.user.last_name}"

	def to_internal_value(self, data):
		data = super().to_internal_value(data)
		state_full_name = data.get('state')
		if state_full_name:
			data['state'] = self.validate_state(state_full_name)
		return data
	
	def validate_state(self, state_full_name):
		if state_full_name in NIGERIAN_STATES:
			return state_full_name
		else:
			raise serializers.ValidationError(f"Invalid state name: {state_full_name}")


class EditPropertySerializer(serializers.ModelSerializer):

	agent_id = serializers.UUIDField()
	owner_id = serializers.UUIDField()
	agent_full_name = serializers.SerializerMethodField()
	owner_full_name = serializers.SerializerMethodField()

	class Meta:
		model = Property
		fields = ['name', 'price', 'amenities', 'description', 'is_verified', 'is_available', 'agent_full_name', 'agent_id', 'owner_full_name','owner_id']

		def update(self, instance, validated_data):
			for attr, value, in validated_data.items():
				setattr(instance, attr, value)
			instance.save()
			return instance

	def get_agent_full_name(self, obj):
		return f"{obj.agent.user.first_name} {obj.agent.user.last_name}"
	
	def get_owner_full_name(self, obj):
		return f"{obj.owner.user.first_name} {obj.owner.user.last_name}"
	

