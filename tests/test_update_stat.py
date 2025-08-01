import json
import pytest

from datetime import date, datetime, timedelta
from types import SimpleNamespace

from crontabs.db.schemas import (
    TransCountryMailCount,
    TransDateCount,
)
from crontabs.scripts.update_stat import Update


async def do_update():
    args = SimpleNamespace(today=True)
    arg_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).date().isoformat()
    dt = datetime.strptime(arg_date, '%Y-%m-%d')
    next_date = (dt + timedelta(days=1)).date().isoformat()

    update = Update(args, arg_date, next_date)
    return update


@pytest.mark.asyncio
async def test_all_registered_users() -> None:
    update = await do_update()
    res = await update.update_all_registered_users()

    assert type(res) is tuple
    assert type(res[0]) is int
    assert type(res[1]) is int


@pytest.mark.asyncio
async def test_trial_user_countries_wo_extension() -> None:
    update = await do_update()
    res = await update.update_trial_user_countries_wo_extension()

    assert type(res) is tuple
    assert type(res[0]) is int

    ext_lst = json.loads(res[1])
    if len(ext_lst) > 0:
        ext = ext_lst[0]
        assert "country" in ext.keys()
        assert "cvalue" in ext.keys()


@pytest.mark.asyncio
async def test_all_active_paid_users() -> None:
    update = await do_update()
    res = await update.update_all_active_paid_users()

    assert type(res) is tuple
    assert type(res[0]) is int
    assert type(res[1]) is int


@pytest.mark.asyncio
async def test_all_active_paid_users_by_plans() -> None:
    update = await do_update()
    res = await update.update_all_active_paid_users_by_plans()

    assert type(res) is tuple
    assert type(res[0]) is int
    assert type(res[1]) is list
    if len(res[1]) > 0:
        for row in res[1]:
            assert type(row.plan) is int or type(row.plan) is str
            assert type(row.count) is int


@pytest.mark.asyncio
async def test_all_active_free_users() -> None:
    update = await do_update()
    res = await update.update_all_active_free_users()

    assert type(res) is tuple
    assert type(res[0]) is int
    assert type(res[1]) is int


@pytest.mark.asyncio
async def test_online_users() -> None:
    update = await do_update()
    res = await update.update_online_users()

    assert type(res) is tuple
    assert type(res[0]) is int
    assert type(res[1]) is int


@pytest.mark.asyncio
async def test_paid_user_countries() -> None:
    update = await do_update()
    res = await update.update_paid_user_countries()

    assert type(res) is tuple
    assert type(res[0]) is int
    assert type(res[1]) is str
    countries = json.loads(res[1])

    for country_ in countries:
        country = TransCountryMailCount(**country_)
        assert type(country.country) is str
        assert type(country.cvalue) is int


@pytest.mark.asyncio
async def test_trial_user_countries_extension_only() -> None:
    update = await do_update()
    res = await update.update_trial_user_countries_extension_only()

    assert type(res) is tuple
    assert type(res[0]) is int
    assert type(res[1]) is str
    countries = json.loads(res[1])

    for country_ in countries:
        country = TransCountryMailCount(**country_)
        assert type(country.country) is str
        assert type(country.cvalue) is int


@pytest.mark.asyncio
async def test_registrations() -> None:
    update = await do_update()
    res = await update.update_registrations()

    assert type(res) is tuple
    assert type(res[0]) is int
    assert type(res[1]) is list

    for row in res[1]:
        assert type(row.date) is datetime
        assert type(row.value) is int


@pytest.mark.asyncio
async def test_trial_registrations_wo_extension_count(ins_del_user_trial) -> None:
    args = SimpleNamespace(today=True)
    arg_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).date().isoformat()
    dt = datetime.strptime(arg_date, '%Y-%m-%d')
    next_date = (dt + timedelta(days=1)).date().isoformat()

    update = Update(args, arg_date, next_date)
    res = await update.update_trial_registrations_wo_extension_count()

    assert type(res) is tuple
    assert type(res[0]) is int
    assert type(res[1]) is list

    for row in res[1]:
        assert type(row.date) is datetime
        assert type(row.value) is int


@pytest.mark.asyncio
async def test_trial_registrations_extension_only_count(ins_del_user_trial) -> None:
    args = SimpleNamespace(today=True)
    arg_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).date().isoformat()
    dt = datetime.strptime(arg_date, '%Y-%m-%d')
    next_date = (dt + timedelta(days=1)).date().isoformat()

    update = Update(args, arg_date, next_date)
    res = await update.update_trial_registrations_extension_only_count()

    assert type(res) is tuple
    assert type(res[0]) is int
    assert type(res[1]) is list

    for row in res[1]:
        assert type(row.date) is date
        assert type(row.cvalue) is int


@pytest.mark.asyncio
async def test_payments_amount(ins_del_payment_amount) -> None:
    args = SimpleNamespace(today=True)
    arg_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).date().isoformat()
    dt = datetime.strptime(arg_date, '%Y-%m-%d')
    next_date = (dt + timedelta(days=1)).date().isoformat()

    update = Update(args, arg_date, next_date)
    res = await update.update_payments_amount()

    assert type(res) is tuple
    assert type(res[0]) is int
    assert type(res[1]) is dict

    for dt in res[1].keys():
        assert type(dt) is date
        val = res[1][dt]
        assert type(val) is dict
        for psystem in val.keys():
            assert type(val[psystem]) is int


@pytest.mark.asyncio
async def test_premium_payments_count(ins_del_payment_amount) -> None:
    args = SimpleNamespace(today=True)
    arg_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).date().isoformat()
    dt = datetime.strptime(arg_date, '%Y-%m-%d')
    next_date = (dt + timedelta(days=1)).date().isoformat()

    update = Update(args, arg_date, next_date)
    res = await update.update_premium_payments_count()

    assert type(res) is tuple
    assert type(res[0]) is int
    assert type(res[1]) is list

    for tdcount in res[1]:
        assert type(tdcount.date) is date
        assert type(tdcount.count) is int


@pytest.mark.asyncio
async def test_trial_payments_wo_extension_count(ins_del_trans_trial_pay_wo_ext) -> None:
    args = SimpleNamespace(today=True)
    arg_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).date().isoformat()
    dt = datetime.strptime(arg_date, '%Y-%m-%d')
    next_date = (dt + timedelta(days=1)).date().isoformat()

    update = Update(args, arg_date, next_date)
    res = await update.update_trial_payments_wo_extension_count()

    assert type(res) is tuple
    assert type(res[0]) is int
    assert type(res[1]) is list

    for tdcount in res[1]:
        assert type(tdcount.date) is date
        assert type(tdcount.count) is int


@pytest.mark.asyncio
async def test_trial_payments_extension_only_count(ins_del_mailtrial_user) -> None:
    args = SimpleNamespace(today=True)
    arg_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).date().isoformat()
    dt = datetime.strptime(arg_date, '%Y-%m-%d')
    next_date = (dt + timedelta(days=1)).date().isoformat()

    update = Update(args, arg_date, next_date)
    res = await update.update_trial_payments_extension_only_count()

    assert type(res) is tuple
    assert type(res[0]) is int
    assert type(res[1]) is list

    for tdcount in res[1]:
        assert type(tdcount.date) is date
        assert type(tdcount.count) is int


@pytest.mark.asyncio
async def test_payments_by_plan(ins_del_mailtrial_user) -> None:
    args = SimpleNamespace(today=True)
    arg_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).date().isoformat()
    dt = datetime.strptime(arg_date, '%Y-%m-%d')
    next_date = (dt + timedelta(days=1)).date().isoformat()

    update = Update(args, arg_date, next_date)
    res = await update.update_payments_by_plan()

    assert type(res) is tuple
    assert type(res[0]) is int
    assert type(res[1]) is list

    for tdcount in res[1]:
        assert type(tdcount.date) is date
        assert type(tdcount.days) is int
        assert type(tdcount.count) is int


@pytest.mark.asyncio
async def test_outcoming_users(ins_trans_outcoming_users) -> None:
    args = SimpleNamespace(today=True)
    arg_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).date().isoformat()
    dt = datetime.strptime(arg_date, '%Y-%m-%d')
    next_date = (dt + timedelta(days=1)).date().isoformat()

    update = Update(args, arg_date, next_date)
    res = await update.update_outcoming_users()

    assert type(res) is tuple
    assert type(res[0]) is dict
    assert type(res[1]) is dict

    for plan in [30, 180, 360, "other"]:
        assert plan in res[0].keys()
        assert type(res[0][plan]) is int

    assert type(list(res[1].keys())[0]) is date
    assert type(list(res[1].values())[0]) is dict
    assert "plan" in list(res[1].values())[0].keys()


@pytest.mark.asyncio
async def test_renewed_users(ins_trans_renewed_users) -> None:
    args = SimpleNamespace(today=True)
    arg_date = (datetime.now() - timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    ).date().isoformat()
    dt = datetime.strptime(arg_date, '%Y-%m-%d')
    next_date = (dt + timedelta(days=1)).date().isoformat()

    update = Update(args, arg_date, next_date)
    res = await update.update_renewed_users()

    assert type(res) is tuple
    assert type(res[0]) is int
    assert type(res[1]) is list

    if len(res[1]) > 0:
        tdc = res[1][0]
        assert type(tdc) is TransDateCount
        assert type(tdc.date) is date
        assert type(tdc.count) is int
