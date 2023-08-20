from django.http import JsonResponse
from ninja import NinjaAPI
from pydantic import BaseModel
from channels.db import database_sync_to_async

from django.contrib.auth import logout, authenticate, login
from server.auth import async_auth

api = NinjaAPI(title="Auth API", version="1.0.0", urls_namespace="auth-api", csrf=True)


class LoginSchema(BaseModel):
    username: str
    password: str


@database_sync_to_async
def _authenticate(username, password):
    return authenticate(username=username, password=password)


@database_sync_to_async
def _login(request, user):
    return login(request, user)


@database_sync_to_async
def _logout(request):
    return logout(request)


@api.post("login/")
async def login_user(request, user_data: LoginSchema):
    user = await _authenticate(user_data.username, user_data.password)
    if user is not None:
        # Django middleware will set the user sessionid in the request cookie
        await _login(request, user)
        return JsonResponse({"detail": "Logged in successfully"})
    return JsonResponse({"error": "Invalid credentials"}, status=401)


@api.post("logout/", auth=async_auth)
async def logout_user(request):
    await _logout(request)
    return JsonResponse({"detail": "Logged out successfully"})


# If we want to use JWTs for authentication, approximate code:
# from datetime import datetime, timedelta
# from jose import JWTError, jwt
# from typing import Optional
# from server import settings
# from django.contrib.auth import get_user_model
# @api.get("access_token/")
# def create_access_token(request) -> str:
#     to_encode = {"username": request.username}
#     expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
#     return encoded_jwt
#
#
# def decode_access_token(token: str) -> Optional[dict]:
#     try:
#         payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
#         return payload
#     except JWTError:
#         return None
#
#
# async def async_auth(request, token: str = None):
#     payload = decode_access_token(token)
#     if payload:
#         return payload
#     return None
