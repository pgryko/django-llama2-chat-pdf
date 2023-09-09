"""
ASGI config for server project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from uvicorn.workers import UvicornWorker
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")

application = get_asgi_application()


class DjangoUvicornWorker(UvicornWorker):
    """
    Generate UvicornWorker with lifespan='off', because Django does not
    (and probably will not https://code.djangoproject.com/ticket/31508)
    support Lifespan.
    Until Django 4.2.x django.core.asgi only handle http
    https://github.com/django/django/blob/stable/4.2.x/django/core/handlers/asgi.py
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Will leave any existing CONFIG_KWARGS in place, and only change the lifespan setting.
        self.config.lifespan = "off"
