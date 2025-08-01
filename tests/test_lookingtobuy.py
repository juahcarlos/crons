import pytest

from datetime import datetime

from libs.utils import subjs, render_tmpl
from crontabs.scripts.lookingtobuy import send_all
from crontabs.db.db_query import BuyFormFill, dbq as db


@pytest.mark.asyncio
async def test_records(ins_del_user_ltb: None) -> None:
    ltb_record = await db.lookingtobuy()

    assert len(ltb_record) > 0
    assert type(ltb_record[0]) is BuyFormFill

    bff = ltb_record[0]
    assert hasattr(bff, "address")
    assert "@" in bff.address


@pytest.mark.asyncio
async def test_subjs() -> None:
    subjects = subjs()
    print("subjects", subjects.keys())
    assert type(subjects) is dict
    assert "lookingtobuy-en" in subjects.keys()
    assert "newcustomer_coupon-en" in subjects.keys()


@pytest.mark.asyncio
async def test_tmpl() -> None:
    data = {'localtime': datetime.now().strftime("%Y")}
    body = render_tmpl("email/lookingtobuy_en.html", data)
    assert "unsubscribe?email" in body


@pytest.mark.asyncio
async def test_send_all(ins_del_user_no_client: None) -> None:
    res = await send_all()
    print("res", res)
    for r in res:
        print("email", r[2])
        assert r[0] == ""
        assert r[1] == 200
