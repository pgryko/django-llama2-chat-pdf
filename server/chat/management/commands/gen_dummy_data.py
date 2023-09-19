from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management.base import BaseCommand

from chat.models import Conversation
from chat.tests.data import DATA_PATH


class Command(BaseCommand):
    help = "Generate a dummy conversation"

    def handle(self, *args, **kwargs):
        Conversation()

        file_path = DATA_PATH / "entropy.pdf"

        SimpleUploadedFile(
            name="entropy.pdf",
            content=file_path.read_bytes(),
            content_type="application/octet-stream",
        )
