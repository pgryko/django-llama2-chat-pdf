from django.db import models
from django.utils.translation import gettext_lazy as _


class MessageTypeChoices(models.TextChoices):
    SYSTEM = "SYSTEM", _("System Message")
    USER = "USER", _("User Message")
    CONTEXT = "CONTEXT", _("VectorDB Context")
    LLM = "LLM", _("LLM Message")
