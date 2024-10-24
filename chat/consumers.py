import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Message, Conversation
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.authentication import JWTAuthentication
import json
from urllib.parse import parse_qs
from django.core.mail import send_mail


User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
	async def connect(self):

		query_params = parse_qs(self.scope['query_string'].decode())
		token = query_params.get('token', [None])[0]
		recipient_user_id = query_params.get('recipient_id', [None])[0]

		self.scope['user'] = await self.authenticate_token(token)

		if self.scope['user'] and self.scope['user'].is_authenticated:
			try:
				self.conversation_id = await self.create_or_get_conversation(self.scope['user'].user_id, recipient_user_id)

				self.room_group_name = f'chat_{self.conversation_id}'

				await self.channel_layer.group_add(
					self.room_group_name,
					self.channel_name
				)

				await self.accept()

				previous_messages = await self.get_previous_messages(self.conversation_id)
				for msg in previous_messages:
					sender_name = await sync_to_async(lambda: msg.sender.first_name if msg.sender.first_name else 'Anonymous')()
					await self.send(text_data=json.dumps({
						'message': msg.message,
						'sender': sender_name
					}))
			except Exception as e:
				await self.send(text_data=json.dumps({
					'error': 'Error during connection: ' + str(e)
				}))
				await self.close()

		else:
			await self.send(text_data=json.dumps({
				'error': 'Invalid or expired token'
			}))

			await self.close()


	async def disconnect(self, close_code):
		if hasattr(self, 'room_group_name'):
			await self.channel_layer.group_discard(
				self.room_group_name,
				self.channel_name
			)


	async def receive(self, text_data):
		data = json.loads(text_data)
		message = data['message']
		user = self.scope["user"]

		conversation = await sync_to_async(Conversation.objects.get)(conversation_id=self.conversation_id)

		new_message = await sync_to_async(Message.objects.create)(
			conversation = conversation,
			sender = user,
			message = message
		)

		await self.notify_recipient(conversation, user, new_message)

		await self.channel_layer.group_send(
			self.room_group_name,
			{
				'type': 'chat_message',
				'message': new_message.message,
				'sender': self.scope['user'].first_name if self.scope['user'].first_name else 'Anonymous',
			}
		)


	async def chat_message(self, event):
		message = event['message']
		sender = event['sender']

		await self.send(text_data=json.dumps({
			'message': message,
			'sender': sender,
		}))

	@sync_to_async
	def get_recipients(self, conversation, sender):
		return list(conversation.participants.exclude(user_id=sender.user_id))

	async def notify_recipient(self, conversation, sender, new_message):
		recipients = await self.get_recipients(conversation, sender)

		for recipient in recipients:
			subject = f"New message from {sender.first_name}"
			message = f"""
			Hi {recipient.first_name}

			You have received a new message from {sender.first_name}:

			"{new_message.message}"

			Login to your account reply.

			"""

			send_mail(subject=subject, message=message, from_email='realestateapp.devteam@gmail.com', recipient_list=[recipient.email], fail_silently=False)


	@sync_to_async
	def authenticate_token(self, token):
		try:
			jwt_auth = JWTAuthentication()
			validated_token = jwt_auth.get_validated_token(token)
			return jwt_auth.get_user(validated_token)
		except (InvalidToken, TokenError) as e:
			return AnonymousUser()
		
	@sync_to_async
	def get_previous_messages(self, conversation_id):
		conversation = Conversation.objects.get(conversation_id=conversation_id)
		return list(Message.objects.filter(conversation=conversation).order_by('timestamp'))
	
	@sync_to_async
	def create_or_get_conversation(self, user_id, recipient_user_id):

		conversation = Conversation.objects.filter(participants__user_id=user_id).filter(participants__user_id=recipient_user_id).distinct()

		if conversation.exists():
			return conversation.first().conversation_id
		
		new_conversation = Conversation.objects.create()
		new_conversation.participants.set([user_id, recipient_user_id])
		new_conversation.save()

		return new_conversation.conversation_id