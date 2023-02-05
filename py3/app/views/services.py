import datetime as dt
from calendar import timegm
from typing import List, Optional

import jwt
from fastapi import HTTPException
from passlib.context import CryptContext

from app import settings as s
from app.services import users

from .models import ListUsersRequest, LoginRequest, LoginResponse, SignUpRequest, User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def make_new_token(user_id, **claims) -> str:
    now = dt.datetime.now(dt.timezone.utc)
    payload = {
        "sub": user_id,
        "iat": timegm(now.utctimetuple()),
        "exp": timegm((now + dt.timedelta(days=s.jwt_expire_in_days)).utctimetuple()),
        **claims,
    }
    return jwt.encode(payload, s.jwt_private_key, algorithm=s.jwt_algo)


def decode_token(t: str):
    class Token:
        def __init__(self, user_id=None, **claims):
            self.user_id = user_id
            self.__dict__.update(**claims)

    try:
        p = jwt.decode(t, s.jwt_public_key, algorithms=[s.jwt_algo])
    except jwt.exceptions.PyJWTError as err:
        raise ValueError("invalid token") from err

    return Token(**p)


def make_password_hash(password):
    return pwd_context.hash(password)


def verify_password(password, pwd_hash):
    return pwd_context.verify(password, pwd_hash)


async def user_login(body: LoginRequest = None) -> LoginResponse:
    if not (user := await users.get_user_with_email(body.email)):
        raise HTTPException(
            status_code=400, detail=f"user with email {body.email} was not found"
        )

    if not verify_password(body.password.get_secret_value(), user.pwd_hash):
        raise HTTPException(status_code=401)

    return LoginResponse(token=make_new_token(user_id=user.user_id))


async def user_sign_up(body: SignUpRequest = None) -> User:
    if await users.get_user_with_email(body.email):
        raise HTTPException(
            status_code=400, detail=f"user with email {body.email} already exists"
        )

    return await users.create_user(
        body.email,
        body.first_name,
        body.last_name,
        body.age,
        body.bio,
        body.city,
        make_password_hash(body.password.get_secret_value()),
    )


async def list_users(filters: Optional[ListUsersRequest] = None) -> List[User]:
    limit = 20
    offset = 0
    first_name = last_name = None
    if filters:
        limit = filters.limit or limit
        offset = filters.offset or offset
        first_name = filters.first_name
        last_name = filters.last_name

    return await users.search_users(first_name, last_name, limit, offset)


async def get_user(id: str) -> User:
    if user := await users.get_user(id):
        return user
    else:
        raise HTTPException(status_code=404)
