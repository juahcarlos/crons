import pytest

from typing import List

from config import settings

from crontabs.db.schemas import UserId, UserReminder
from crontabs.lib.utils import get_emails, get_users, get_unsubscribe_token
from crontabs.lib.mail import render_body_reminder, send_all_reminder


@pytest.mark.asyncio
async def test_tmpl(users_from_db: List[UserId]) -> None:
    body = await render_body_reminder(users_from_db[0])
    assert "2008-" in body


@pytest.mark.asyncio
async def test_token() -> None:
    token = get_unsubscribe_token(settings.TEST_EMAIL)
    assert token == settings.TEST_TOKEN


@pytest.mark.asyncio
async def test_get_emails(ins_del_user_no_client: None) -> None:
    result = await get_emails(settings.TEST_EMAIL)
    assert type(result) is list
    assert len(result) > 0
    assert type(result[0]) is UserId
    assert result[0].email == settings.TEST_EMAIL


@pytest.mark.asyncio
async def test_get_users(users_from_db: List[UserId]) -> None:
    result = await get_users(users_from_db)
    assert type(result) is list
    assert len(result) > 0
    assert type(result[0]) is UserReminder
    assert result[0].email == settings.TEST_EMAIL


@pytest.mark.asyncio
async def test_send_all(ins_del_user_no_client: None, users_from_db: List[UserId]) -> None:
    res = await send_all_reminder(users_from_db)
    print("res", res)

    for r in res:
        print("email", r[2])
        assert r[0] == "" or r[0] is None
        assert r[1] == 200
