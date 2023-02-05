import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from . import services
from .models import ListUsersRequest, LoginRequest, LoginResponse, SignUpRequest, User

app = FastAPI(
    title="Highload Research Project -- Social Network",
    version="0.1.0",
    servers=[
        {
            "url": "https://{hostname}/",
            "variables": {"hostname": {"default": "localhost"}},
        }
    ],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        claims = services.decode_token(token)
    except ValueError:
        raise credentials_exception

    return claims.user_id


@app.post("/auth/login", response_model=LoginResponse)
async def user_login(body: LoginRequest = None) -> LoginResponse:
    return await services.user_login(
        body,
    )


@app.post("/auth/signup", response_model=User)
async def user_sign_up(body: SignUpRequest = None) -> User:
    return await services.user_sign_up(
        body,
    )


@app.get("/users/", response_model=list[User])
async def list_users(
    filters: ListUsersRequest = Depends(), _: str = Depends(get_current_user)
) -> list[User]:
    return await services.list_users(
        filters,
    )


@app.get("/users/{id}", response_model=User)
async def get_user(id: str, _: str = Depends(get_current_user)) -> User:
    return await services.get_user(
        id,
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
