import datetime as dt
from calendar import timegm

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app import settings as s

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")



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
    class Claims:
        def __init__(self, user_id=None, **claims):
            self.user_id = user_id
            self.__dict__.update(**claims)

    try:
        p = jwt.decode(t, s.jwt_public_key, algorithms=[s.jwt_algo])
    except jwt.exceptions.PyJWTError as err:
        raise ValueError("invalid token") from err

    return Claims(**p)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        claims = decode_token(token)
    except ValueError:
        raise credentials_exception

    return claims.user_id
