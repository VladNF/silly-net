import pytest

from app.services.users import get_user_with_email

pytestmark = [pytest.mark.asyncio]

@pytest.mark.in_mem_repo
async def test_basic_signup_ok(web_app):
    r = await web_app.post(
        "/auth/signup",
        json={
            "email": "j@VladNF.ru",
            "first_name": "Vlad",
            "last_name": "NF",
            "age": 42,
            "bio": "somewhere in the deep space",
            "city": "NF",
            "password": "424242",
        }
    )

    assert r.status_code == 200
    assert r.json()["user_id"]
    assert r.json()["token"]
    assert (u := await get_user_with_email("j@VladNF.ru"))
    assert u.email == "j@VladNF.ru".lower()
    assert u.first_name == "Vlad"
    assert u.last_name == "NF"
    assert u.age == 42
    assert u.city == "NF"


@pytest.mark.in_mem_repo
async def test_login_ok(web_app, user_1):
    r = await web_app.post(
        "/auth/login",
        json={
            "email": user_1.email,
            "password": "424242",
        }
    )

    assert r.status_code == 200
    assert r.json()["token"]
