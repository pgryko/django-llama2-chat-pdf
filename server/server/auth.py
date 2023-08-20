from channels.db import database_sync_to_async
from django.http import HttpRequest
from django.contrib import auth


async def async_auth(request: HttpRequest):
    user = await database_sync_to_async(auth.get_user)(request)
    # async auth merged to main Mar 2023 but not released yet
    # https://github.com/django/django/pull/16552/files
    # https://github.com/bigfootjon/django/blob/e846c5e7246a0ffbe5dcf07a2b6c7c2a47537eb3/django/contrib/auth/middleware.py
    # leave this placeholder code here for now
    # user = await request.auser()
    if user.is_authenticated:
        return user

    return None
