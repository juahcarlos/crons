import argparse
import httpx
import pytest_asyncio

import sys

from datetime import datetime, timedelta
from pathlib import Path
from typing import AsyncGenerator, List, Tuple

from config import settings
from libs.logs import log
from crontabs.db.schemas import User, UserId
from crontabs.db.db_query import dbq as db
from dbm.schemas import TransactionFull

for n in [2, 3]:
    sys.path.append(str(Path(__file__).parents[n]))
    print(Path(__file__).parents[n])


def userr() -> User:
    return User(
        email=settings.TEST_EMAIL,
        created=datetime.now() - timedelta(hours=1),
        code=settings.TEST_CODE,
        trial=False,
        plan=settings.TEST_PLAN,
        lang=settings.TEST_LANG,
        expires=int((datetime.now() + timedelta(days=30)).strftime("%s"))
    )


def user_trial() -> User:
    return User(
        email=settings.TEST_EMAIL,
        created=datetime.now(),
        code=settings.TEST_CODE,
        trial=True,
        plan=settings.TEST_PLAN,
        lang=settings.TEST_LANG,
        expires=int((datetime.now() + timedelta(days=30)).strftime("%s"))
    )


def user_mailtrial() -> User:
    return User(
        email=settings.TEST_EMAIL_TRIAL,
        created=datetime.now(),
        code=settings.TEST_CODE,
        trial=True,
        plan=settings.TEST_PLAN,
        lang=settings.TEST_LANG,
        expires=int((datetime.now() + timedelta(days=30)).strftime("%s"))
    )


def trans_mailtrial() -> TransactionFull:
    return TransactionFull(
        system="freekassa",
        data="{}",
        days=30,
        amount=9.9,
        email=settings.TEST_EMAIL_TRIAL,
        created=datetime.now(),
        expires=datetime.now() + timedelta(days=30),
        coupon=None,
        trial=True,
        version_page=2,
        country_iso="en",
        complete=1,
    )


def trans_cust_promo() -> TransactionFull:
    return TransactionFull(
        system="freekassa",
        data="{}",
        days=30,
        amount=9.9,
        email=settings.TEST_EMAIL,
        created=datetime.now() - timedelta(days=23),
        expires=datetime.now() + timedelta(days=7) - timedelta(minutes=30),
        coupon=None,
        trial=False,
        version_page=2,
        country_iso="en",
        complete=1,
    )


def trans_cust_coupon() -> TransactionFull:
    return TransactionFull(
        system="freekassa",
        data="{}",
        days=30,
        amount=9.9,
        email=settings.TEST_EMAIL,
        created=datetime.now() - timedelta(days=1) - timedelta(minutes=30),
        expires=datetime.now() + timedelta(days=29),
        coupon=None,
        trial=True,
        version_page=2,
        country_iso="en",
        complete=1,
    )


def trans_trial_payments_wo_extension() -> TransactionFull:
    return TransactionFull(
        system="freekassa",
        data="{}",
        days=30,
        amount=9.9,
        email=settings.TEST_EMAIL,
        created=datetime.now(),
        expires=datetime.now() + timedelta(days=29),
        coupon=None,
        trial=True,
        version_page=2,
        country_iso="en",
        complete=1,
    )


def user_lookingtobuy() -> User:
    return User(
        email=settings.TEST_EMAIL,
        created=datetime.now() - timedelta(minutes=90),
        code=settings.TEST_CODE,
        trial=False,
        plan=settings.TEST_PLAN,
        lang=settings.TEST_LANG,
        expires=int(datetime.now().strftime("%s"))
    )


def user_churn() -> User:
    return User(
        email=settings.TEST_EMAIL,
        created=datetime(2018, 6, 1),
        expires=int(datetime(2018, 12, 1).strftime("%s")),
        code=settings.TEST_CODE,
        trial=False,
        plan=settings.TEST_PLAN,
        lang=settings.TEST_LANG
    )


def trans_churn2() -> TransactionFull:
    return TransactionFull(
        system="freekassa",
        data="{}",
        days=30,
        amount=9.9,
        email=settings.TEST_EMAIL,
        created=datetime(2018, 6, 1),
        expires=datetime(2019, 2, 1),
        coupon=None,
        trial=False,
        version_page=2,
        country_iso="en",
        complete=1,
    )


def trans_lookingtobuy() -> TransactionFull:
    return TransactionFull(
        system="freekassa",
        data="{}",
        days=30,
        amount=9.9,
        email=settings.TEST_EMAIL,
        created=datetime.now() - timedelta(minutes=110),
        expires=datetime.now() + timedelta(days=30),
        coupon=None,
        trial=False,
        version_page=2,
        country_iso="en",
        complete=0,
    )


def trans_churn() -> TransactionFull:
    return TransactionFull(
        system="freekassa",
        data="{}",
        days=30,
        amount=9.9,
        email=settings.TEST_EMAIL,
        created=datetime(2017, 12, 1),
        expires=datetime(2018, 2, 1),
        coupon=None,
        trial=False,
        version_page=2,
        country_iso="en",
        complete=1,
    )


def trans_payment_amounts() -> TransactionFull:
    return TransactionFull(
        system="freekassa",
        data="{}",
        days=30,
        amount=9.9,
        email=settings.TEST_EMAIL,
        created=datetime.now(),
        expires=datetime.now() + timedelta(days=30),
        coupon=None,
        trial=False,
        version_page=2,
        country_iso="en",
        complete=1,
    )


def trans_outcoming_users() -> TransactionFull:
    return TransactionFull(
        system="freekassa",
        data="{}",
        days=30,
        amount=9.9,
        email=settings.TEST_EMAIL,
        created=datetime.now().date(),
        expires=datetime.now().date() + timedelta(seconds=30),
        coupon=None,
        trial=False,
        version_page=2,
        country_iso="en",
        complete=1,
    )


def trans_renewed_users() -> TransactionFull:
    return TransactionFull(
        system="freekassa",
        data="{}",
        days=30,
        amount=9.9,
        email=settings.TEST_EMAIL,
        created=datetime.now() + timedelta(days=1),
        expires=datetime.now() + timedelta(days=30),
        coupon=None,
        trial=False,
        version_page=2,
        country_iso="en",
        complete=1,
    )


def trans_renewed_users2() -> TransactionFull:
    return TransactionFull(
        system="freekassa",
        data="{}",
        days=30,
        amount=9.9,
        email=settings.TEST_EMAIL,
        created=datetime.now() - timedelta(days=31),
        expires=datetime.now() - timedelta(days=2),
        coupon=None,
        trial=False,
        version_page=2,
        country_iso="en",
        complete=1,
    )


@pytest_asyncio.fixture()
async def test_args_user() -> argparse.Namespace:
    mock_args = argparse.Namespace(
        user=settings.TEST_EMAIL,
        all=None,

    )
    return mock_args


@pytest_asyncio.fixture()
async def test_args_email() -> argparse.Namespace:
    mock_args = argparse.Namespace(
        email=settings.TEST_EMAIL,
        all=None,
    )
    return mock_args


@pytest_asyncio.fixture()
async def test_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """creates and yeild client for http requests
    """
    async with httpx.AsyncClient() as client:
        yield client


@pytest_asyncio.fixture()
async def users() -> str:
    return [settings.TEST_EMAIL]


@pytest_asyncio.fixture()
async def users_from_db() -> List[UserId]:
    return [
        UserId(
            email='senyadostoeffsky@gmail.com',
            created='2024-03-01 18:58:40',
            cn='sec2417586',
            trial=None,
            version_page=None,
            code=None,
            coupon=None,
            expires=0,
            plan=30,
            country_iso=None,
            password=None,
            reg_source=None,
            dubious=0,
            ubscribed=0,
            lang='ru',
            partner_id=None,
            note=None, id=2417586
        )
    ]


async def insert_user(user) -> None:
    await db.delete_user(settings.TEST_EMAIL)
    await db.insert_email(user)
    get_new_user = await db.get_user_db(settings.TEST_EMAIL)
    print(f"\n\n *************** get_new_user {get_new_user} {get_new_user.__dict__}\n\n")
    await db.update_user_after_insert(get_new_user)


async def delete_user() -> None:
    await db.delete_user(settings.TEST_EMAIL)
    await db.delete_lookingtobuy(settings.TEST_EMAIL)


@pytest_asyncio.fixture()
async def test_client_ins_del_user(user) -> AsyncGenerator[httpx.AsyncClient, None]:
    """inserts user,
    creates and yeild client for http requests,
    deletes user
    """
    user_ = user()
    await insert_user(user_)

    async with httpx.AsyncClient() as client:
        print(f"\n\n insert_email test_client_ins_del_user client {client}\n\n")
        yield client

    await delete_user()


@pytest_asyncio.fixture
async def ins_del_user() -> AsyncGenerator[UserId, None]:
    user_ = userr()
    await insert_user(user_)

    user_ret = await db.get_user_by_email(settings.TEST_EMAIL)
    yield user_ret

    await delete_user()


@pytest_asyncio.fixture
async def ins_del_mailtrial_user() -> AsyncGenerator[UserId, None]:
    user_ = user_mailtrial()
    print(f"******************* user_ {user_}")
    await db.delete_user(settings.TEST_EMAIL_TRIAL)
    await db.insert_email(user_)
    user_ret = await db.get_user_by_email(settings.TEST_EMAIL_TRIAL)

    trans_data = trans_mailtrial()
    trans = await db.insert_transaction(trans_data)

    print(f"******************* user_ret {user_ret}")
    yield user_ret

    await delete_user()
    await db.delete_trans_by_id(trans.id)


@pytest_asyncio.fixture
async def ins_del_user_trial() -> AsyncGenerator[UserId, None]:
    user_ = user_trial()
    await insert_user(user_)

    user_ret = await db.get_user_by_email(settings.TEST_EMAIL)
    yield user_ret

    await delete_user()


@pytest_asyncio.fixture()
async def ins_del_user_no_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """inserts user,
    yeild None,
    deletes user
    """
    user_ = userr()
    await insert_user(user_)

    yield None

    await delete_user()


@pytest_asyncio.fixture
async def ins_del_user_nc_promo() -> AsyncGenerator[UserId, None]:
    user_data = userr()
    await insert_user(user_data)
    trans_data = trans_cust_promo()
    trans = await db.insert_transaction(trans_data)
    log.debug(f"--------------- fixture trans {trans}")

    user_ret = await db.get_user_by_email(settings.TEST_EMAIL)
    yield user_ret

    await delete_user()
    await db.delete_trans_by_id(trans.id)


@pytest_asyncio.fixture
async def ins_del_trans_trial_pay_wo_ext() -> AsyncGenerator[UserId, None]:
    user_data = userr()
    await insert_user(user_data)
    trans_data = trans_trial_payments_wo_extension()
    trans = await db.insert_transaction(trans_data)
    log.debug(f"--------------- fixture trans {trans}")

    user_ret = await db.get_user_by_email(settings.TEST_EMAIL)
    yield user_ret

    await delete_user()
    await db.delete_trans_by_id(trans.id)


@pytest_asyncio.fixture
async def ins_del_user_nc_coupon() -> AsyncGenerator[UserId, None]:
    user_data = userr()
    await insert_user(user_data)
    trans_data = trans_cust_coupon()
    trans = await db.insert_transaction(trans_data)
    log.debug(f"--------------- fixture trans {trans}")

    user_ret = await db.get_user_by_email(settings.TEST_EMAIL)
    yield user_ret

    await delete_user()
    await db.delete_trans_by_id(trans.id)


@pytest_asyncio.fixture
async def ins_del_payment_amount() -> AsyncGenerator[UserId, None]:
    user_data = userr()
    await insert_user(user_data)
    trans_data = trans_payment_amounts()
    trans = await db.insert_transaction(trans_data)
    log.debug(f"--------------- fixture trans {trans}")

    user_ret = await db.get_user_by_email(settings.TEST_EMAIL)
    yield user_ret

    await delete_user()
    await db.delete_trans_by_id(trans.id)


@pytest_asyncio.fixture
async def ins_del_user_ltb() -> AsyncGenerator[UserId, None]:
    user_data = user_lookingtobuy()
    await db.delete_user(settings.TEST_EMAIL)
    await insert_user(user_data)
    trans_data = trans_lookingtobuy()
    trans = await db.insert_transaction(trans_data)

    user_ret = await db.get_user_by_email(settings.TEST_EMAIL)

    yield user_ret

    await delete_user()
    await db.delete_trans_by_id(trans.id)


@pytest_asyncio.fixture
async def ins_del_churn() -> AsyncGenerator[Tuple[UserId, TransactionFull, TransactionFull], None]:
    user_data = user_churn()
    await db.delete_user(settings.TEST_EMAIL)
    await insert_user(user_data)
    trans_data = trans_churn()
    trans = await db.insert_transaction(trans_data)
    trans_data2 = trans_churn2()
    trans2 = await db.insert_transaction(trans_data2)

    user_ret = await db.get_user_by_email(settings.TEST_EMAIL)

    yield user_ret, trans, trans2

    await delete_user()
    await db.delete_trans_by_id(trans.id)
    await db.delete_trans_by_id(trans2.id)


@pytest_asyncio.fixture
async def ins_trans_outcoming_users() -> AsyncGenerator[TransactionFull, None]:
    trans_data = trans_outcoming_users()
    trans = await db.insert_transaction(trans_data)
    yield trans
    await db.delete_trans_by_id(trans.id)


@pytest_asyncio.fixture
async def ins_trans_renewed_users() -> AsyncGenerator[Tuple[TransactionFull, TransactionFull], None]:
    trans_data = trans_renewed_users()
    trans = await db.insert_transaction(trans_data)
    trans_data2 = trans_renewed_users2()
    trans2 = await db.insert_transaction(trans_data2)
    yield trans, trans2
    await db.delete_trans_by_id(trans.id)
    await db.delete_trans_by_id(trans2.id)
