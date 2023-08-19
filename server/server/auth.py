from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional

from django.contrib.auth import get_user_model, logout

SECRET_KEY = (
    "YOUR_SECRET_KEY"  # This should be kept secret and can be moved to Django settings
)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # You can adjust this as needed

from django.contrib.auth import authenticate, login


def login_user(request, username, password):
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return user
    return None


def logout_user(request):
    logout(request)


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


async def async_auth(request, token: str = None):
    payload = decode_access_token(token)
    if payload:
        return payload
    return None
