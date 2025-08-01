
import pytest

from config import settings
from crontabs.scripts.sync_softether_users import get_users, sync_softether


@pytest.mark.asyncio
async def test_get_users(test_args_user, ins_del_user_no_client) -> None:
    result = await get_users(test_args_user)
    assert type(result) is list
    assert len(result) > 0
    assert result[0].email == settings.TEST_EMAIL


@pytest.mark.asyncio
async def test_sync(test_args_user, ins_del_user_no_client) -> None:
    users = await get_users(test_args_user)
    with pytest.raises(Exception):
        await sync_softether(users, settings.TEST_SERVER)
