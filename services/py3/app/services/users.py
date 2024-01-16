from ..models.users import User
from ..repo.users import users_repo


async def get_user(user_id: str) -> User:
    return await users_repo.get(user_id)


async def get_user_with_email(email: str) -> User:
    return await users_repo.get_by_email(email.lower())


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
    return await users_repo.get_multi(first_name, last_name, limit, offset)
