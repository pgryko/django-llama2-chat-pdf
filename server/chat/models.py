import uuid

from django.contrib.auth import get_user_model
from django.db import models

from server.models import TimeStampField

User = get_user_model()


class ChromaDBCollection(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4)

    class Meta:
        managed = (
            False  # This ensures Django won't create a database table for this model
        )


class Conversation(TimeStampField):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    collection = models.UUIDField(default=uuid.uuid4)

    class Meta:
        ordering = ["-updated_at"]


class Message(TimeStampField):
    TYPE_CHOICES = (
        ("SYS", "System Message"),
        ("USER", "User Message"),
        ("CONTEXT", "Vector DB Context"),
        ("LLM", "LLM Response"),
    )
    conversation = models.ForeignKey(
        Conversation, related_name="messages", on_delete=models.CASCADE
    )
    message_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    content = models.TextField()

    class Meta:
        ordering = ["-updated_at"]
