import pytest

import warnings
import urllib3

from crontabs.db.schemas import VpnStat
from crontabs.scripts.vpn_get_online_users_and_bw import get_stat


def setup_module(module):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    warnings.filterwarnings("ignore", category=urllib3.exceptions.InsecureRequestWarning)


@pytest.mark.asyncio
async def test_stat() -> None:
    res = await get_stat()
    # res = await db.get_user_by_email("avikougan@gmail.com")
    print(f"res {res}")

    assert type(res) is VpnStat
    assert type(res.wman_version) is str
    assert res.online_vpn >= 0
