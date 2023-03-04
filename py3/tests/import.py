"""
Import users from tests/people.csv
"""
import asyncio
from itertools import islice

from app.models.users import User, make_unique_id
from app.repo.users import make_new_repo


BATCH_SIZE = 100


def people_lines():
    with open("./tests/people.csv") as f:
        yield from f


def batched(iterable):
    it = iter(iterable)
    while batch := tuple(islice(it, BATCH_SIZE)):
        yield batch


def as_user(line: str):
    name, age, city = line.rstrip("\n").split(",")
    last, first = name.split()
    user_id = make_unique_id()
    return User(
        user_id=user_id,
        first_name=first,
        last_name=last,
        age=int(age),
        city=city,
        email=f"{user_id}@email.com",
    )


async def import_users():
    users_added = 0
    r = make_new_repo()
    print("Start importing users...")
    for lines in batched(people_lines()):
        await r.put_multi(map(as_user, lines))
        users_added += BATCH_SIZE
        print(f"Users added so far ....{users_added}")


if __name__ == "__main__":
    asyncio.run(import_users())
