import random
import uuid

from locust import HttpUser, task, between


RU_SYMBOLS = "абвгдежзийклмнопрстуфхцчшщьъэюя"
SEARCH_TERM_LEN = [2, 3, 4, 5, 6, 7]


def random_search_term():
    k = random.choice(SEARCH_TERM_LEN)
    chars = random.choices(RU_SYMBOLS, k=k)
    return "".join(chars)


class ReadOnlyLoad(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        r = self.client.post(
            "/auth/signup",
            json={
                "email": f"{uuid.uuid4().hex}@VladNF.ru",
                "first_name": "Vlad",
                "last_name": "NF",
                "age": 42,
                "bio": "somewhere in the deep space",
                "city": "NF",
                "password": "424242",
            },
            name="signup",
        )
        assert r.ok
        token = r.json()["token"]
        self.client.headers = {"Authorization": f"Bearer {token}"}

    @task
    def search_people(self):
        self.client.get(
            f"/users/?first_name={random_search_term()}&last_name={random_search_term()}",
            name="search",
        )


class WriteOnlyLoad(HttpUser):
    wait_time = between(1, 2)

    @task
    def sign_up(self):
        r = self.client.post(
            "/auth/signup",
            json={
                "email": f"{uuid.uuid4().hex}@VladNF.ru",
                "first_name": "Vlad",
                "last_name": "NF",
                "age": 42,
                "bio": "somewhere in the deep space",
                "city": "NF",
                "password": "424242",
            },
            name="signup",
        )
        assert r.ok
