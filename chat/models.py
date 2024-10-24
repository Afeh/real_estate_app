from django.db import models
from django.contrib.auth import get_user_model
import uuid
from authentication.models import User



class Conversation(models.Model):
	conversation_id = models.UUIDField(default=uuid.uuid4, primary_key=True)
	participants = models.ManyToManyField(User)
	created_at = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
	message_id = models.UUIDField(default=uuid.uuid4, primary_key=True)
	conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
	sender = models.ForeignKey(User, on_delete=models.CASCADE)
	message = models.TextField()
	timestamp = models.DateTimeField(auto_now_add=True)
