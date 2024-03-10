import pytest

pytestmark = [pytest.mark.asyncio]


@pytest.mark.in_mem_repo
async def test_basic_search_ok(web_app, users, valid_token):
    r = await web_app.get(
        "/users/",
        headers={"Authorization": f"Bearer {valid_token}"},
        params={
            "first_name": "Vlad",
            "last_name": "NF",
        },
    )

    assert r.status_code == 200
    assert (users := r.json()) and len(users) == 1
    u = users[0]
    assert u["email"] == "j@VladNF.ru".lower()
    assert u["first_name"] == "Vlad"
    assert u["last_name"] == "NF"
    assert u["age"] == 42
    assert u["city"] == "NF"


@pytest.mark.in_mem_repo
async def test_search_empty_ok(web_app, valid_token):
    r = await web_app.get(
        "/users/",
        headers={"Authorization": f"Bearer {valid_token}"},
        params={
            "first_name": "John",
            "last_name": "WA",
        },
    )

    assert r.status_code == 200
    assert not r.json()


@pytest.mark.in_mem_repo
@pytest.mark.parametrize("limit, offset, count", [(0, 0, 1), (1, 0, 1), (5, 5, 0)])
async def test_search_paging_ok(web_app, users, valid_token, limit, offset, count):
    r = await web_app.get(
        "/users/",
        headers={"Authorization": f"Bearer {valid_token}"},
        params={
            "first_name": "Vlad",
            "last_name": "NF",
            "limit": limit,
            "offset": offset,
        },
    )

    assert r.status_code == 200
    assert len(r.json()) == count
