from typing import List, Optional

from fastapi import HTTPException

from app.services import users
from .auth import make_new_token
from .models import ListUsersRequest, LoginRequest, LoginResponse, SignUpRequest, SignUpResponse, User


async def user_login(body: LoginRequest = None) -> LoginResponse:
    if not (user := await users.get_user_with_email(body.email)):
        raise HTTPException(
            status_code=400, detail=f"user with email {body.email} was not found"
        )

    if not users.verify_password(body.password.get_secret_value(), user.pwd_hash):
        raise HTTPException(status_code=401)

    return LoginResponse(token=make_new_token(user_id=user.user_id))


async def user_sign_up(body: SignUpRequest = None) -> SignUpResponse:
    if await users.get_user_with_email(body.email):
        raise HTTPException(
            status_code=400, detail=f"user with email {body.email} already exists"
        )

    user = await users.create_user(
        body.email,
        body.first_name,
        body.last_name,
        body.age,
        body.bio,
        body.city,
        users.make_password_hash(body.password.get_secret_value()),
    )
    return SignUpResponse(**user.dict(), token=make_new_token(user_id=user.user_id))


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
