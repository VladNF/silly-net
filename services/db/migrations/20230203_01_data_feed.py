#
# file: migrations/20230203_01_data_feed.py
#
import uuid
from collections import namedtuple
from itertools import islice

from yoyo import step


__depends__ = {"20230202_01_init"}

# create table users
# (
#     user_id    varchar(32) primary key,
#     email      text unique,
#     first_name text,
#     last_name  text,
#     age        integer,
#     bio        text,
#     city       text,
#     pwd_hash   text
# );

User = namedtuple(
    "User", "user_id, email, first_name, last_name, age, city, pwd_hash"
)
BATCH_SIZE = 1_000


def make_unique_id():
    """Make a new UniqueId."""
    return uuid.uuid4().hex


def people_lines():
    with open("./migrations/feeds/people.csv") as f:
        yield from f


def batched(iterable):
    it = iter(iterable)
    while batch := tuple(islice(it, BATCH_SIZE)):
        yield batch


def as_user_tuple(line: str) -> str:
    name, age, city = line.rstrip("\n").split(",")
    last, first = name.split()
    user_id = make_unique_id()
    u = User(
        user_id=user_id,
        first_name=first,
        last_name=last,
        age=int(age),
        city=city,
        email=f"{user_id}@email.com",
        pwd_hash="====generated====",
    )

    return str(tuple(u))


def import_users(cursor):
    users_added = 0
    print("Start importing users...")
    for lines in batched(people_lines()):
        query = f"""
        insert into users(user_id, email, first_name, last_name, age, city, pwd_hash)
        values {", ".join(map(as_user_tuple, lines))}
        """
        cursor.execute(query)
        users_added += BATCH_SIZE
        print(f"Users added so far ....{users_added}")


def apply_step(conn):
    cursor = conn.cursor()
    import_users(cursor)


def rollback_step(conn):
    cursor = conn.cursor()
    cursor.execute("delete from users where pwd_hash='====generated===='")


steps = [step(apply_step, rollback_step)]
