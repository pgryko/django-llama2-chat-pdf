# Create your models here.
from django.contrib.auth.models import (
    AbstractUser,
)

# For Django its best practice to create a custom user class when a project starts
# It allows for easier customisation later on in the project

class AccountUser(AbstractUser):
    ...
