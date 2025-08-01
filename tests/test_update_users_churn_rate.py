
import pytest

from datetime import datetime

from crontabs.db.schemas import ChurnRate
from crontabs.scripts.update_active_users_churn_rate \
    import process_year_stat, process_month_stat


@pytest.mark.asyncio
async def test_process_year_stat(ins_del_churn) -> None:
    now = datetime.now()
    res = await process_year_stat(now.year)

    assert type(res) is ChurnRate
    assert type(res.users_in_end_of_prev_period) is int
    assert res.users_in_end_of_prev_period >= 0
    assert type(res.churn_rate) is float


@pytest.mark.asyncio
async def test_process_month_stat() -> None:
    now = datetime.now()
    print(now.year, now.month)
    res = await process_month_stat(now.year, now.month)

    if res is not None:
        assert type(res) is ChurnRate
        assert type(res.users_in_end_of_prev_period) is int
        assert res.users_in_end_of_prev_period >= 0
        assert type(res.churn_rate) is float
