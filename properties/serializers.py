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
	agent_id = serializers.UUIDField()
	owner_id = serializers.UUIDField()

	class Meta:
		model = Property
		fields = ['property_id', 'state', 'name', 'address', 'longitude', 'latitude', 'price', 'amenities', 'bedroom_number', 'bathroom_number', 'description', 'agent_id', 'owner_id']

		def validate(self, data):
			state_full_name = data.get('state')
			if state_full_name in NIGERIAN_STATES:
				data['state'] = NIGERIAN_STATES[state_full_name]
			else:
				raise serializers.ValidationError(f"Invalid state name: {state_full_name}")
			return data