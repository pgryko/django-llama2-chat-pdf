from datetime import timedelta

from django.contrib.auth import authenticate, login
from ninja import NinjaAPI
from pydantic import BaseModel

from server.auth import create_access_token


# Define your secret key and algorithm
SECRET_KEY = "YOUR_SECRET_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

api = NinjaAPI(
    title="Auth API",
    version="1.0.0",
    urls_namespace="auth-api",
)


class LoginSchema(BaseModel):
    username: str
    password: str


@api.post("/login/")
def login_view(request, data: LoginSchema):
    user = authenticate(request, username=data.username, password=data.password)
    if user is not None:
        login(request, user)
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    return 401, {"message": "Invalid credentials"}
