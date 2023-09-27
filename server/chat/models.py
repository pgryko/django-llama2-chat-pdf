import uuid

from django.contrib.auth import get_user_model
from django.db import models

from chat.enums import MessageTypeChoices
from server.models import TimeStampField

User = get_user_model()


class ChromaDBCollection(models.Model):
    # ID used by chromadb
    chroma_id = models.UUIDField(default=uuid.uuid4)
    # Name that we used to create the collection, we should standardize on UUIDs
    name = models.CharField(max_length=255)
    count = models.IntegerField(default=0)

    # Fist 10 items in the collection
    peek = models.JSONField(default=dict)


class Conversation(TimeStampField):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    collection = models.UUIDField(default=uuid.uuid4)

    class Meta:
        ordering = ["-updated_at"]


class DocumentFile(TimeStampField):
    file = models.FileField(upload_to="user_files/")
    md5 = models.CharField(max_length=32, blank=True, null=True)
    original_name = models.CharField(max_length=255, blank=True, null=True)

    conversation = models.ForeignKey(
        Conversation, related_name="documentfiles", on_delete=models.CASCADE
    )

    def delete(self, *args, **kwargs):
        # Delete the file before removing the model instance
        storage, path = self.file.storage, self.file.path
        storage.delete(path)

        # Call the superclass' delete method to remove the model instance
        super(DocumentFile, self).delete(*args, **kwargs)


class Message(TimeStampField):
    conversation = models.ForeignKey(
        Conversation, related_name="messages", on_delete=models.CASCADE
    )
    message_type = models.CharField(max_length=10, choices=MessageTypeChoices.choices)
    content = models.TextField()

    class Meta:
        ordering = ["updated_at"]
