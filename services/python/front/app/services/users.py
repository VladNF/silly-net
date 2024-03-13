from passlib.context import CryptContext

from ..models.users import User
from ..repo.users import users_repo, users_repo_ro

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def get_user(user_id: str) -> User:
    return await users_repo_ro.get(user_id)


async def get_user_with_email(email: str) -> User:
    return await users_repo_ro.get_by_email(email.lower())


async def create_user(email, first_name, last_name, age, bio, city, pwd_hash) -> User:
    user = User(
        email=email.lower(),
        first_name=first_name,
        last_name=last_name,
        age=age,
        bio=bio,
        city=city,
        pwd_hash=pwd_hash,
    )
    return await users_repo.put(user)


async def search_users(first_name, last_name, limit, offset) -> list[User]:
    return await users_repo_ro.get_multi(first_name, last_name, limit, offset)


def make_password_hash(password):
    return pwd_context.hash(password)


def verify_password(password, pwd_hash):
    return pwd_context.verify(password, pwd_hash)
