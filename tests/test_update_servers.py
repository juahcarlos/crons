
import json
import pytest

from crontabs.config_cron import settings

from crontabs.scripts.vpn_update_servers import (
    get_users, get_servers, get_json_data, post_update, post_ips
)


@pytest.mark.asyncio
async def test_get_users(test_args_email, ins_del_user_no_client) -> None:
    result = await get_users(test_args_email)
    assert type(result) is list
    assert len(result) > 0
    assert result[0].email == settings.TEST_EMAIL


@pytest.mark.asyncio
async def test_get_servers() -> None:
    result = await get_servers()
    assert type(result) is dict
    assert len(result.keys()) > 0
    print(f"result {result.keys()}")
    assert type(list(result.keys())[0]) is str


@pytest.mark.asyncio
async def test_get_json_data(test_args_email, ins_del_user_no_client) -> None:
    users = await get_users(test_args_email)
    result = await get_json_data(users)
    print("**************** result", result)
    for res in result:
        if res != []:
            r = json.loads(res[0])
            assert users[0].cn in r.keys()


@pytest.mark.asyncio
async def test_post_update(test_args_email, ins_del_user_no_client) -> None:
    users = await get_users(test_args_email)
    json_data = await get_json_data(users)
    servers = await get_servers()
    result = await post_update(json.loads(json_data[0][0]), servers[settings.TEST_SERVER])
    assert result.status_code == 200 or result.status_code == 500


@pytest.mark.asyncio
async def test_post_ips(test_args_email, ins_del_user_no_client) -> None:
    servers = await get_servers()
    result = await post_ips(servers)

    if result is not None:
        assert result.status_code == 200 or result.status_code == 500
        assert result.content == b'1'
