# Create your models here.
import uuid
from django.contrib.auth.models import (
    AbstractUser,
)
from django.db import models

from server.models import TimeStampField


# For Django its best practice to create a custom user class when a project starts
# It allows for easier customization later on in the project


class AccountUser(AbstractUser, TimeStampField):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
