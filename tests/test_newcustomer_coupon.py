import pytest

from config import settings

from crontabs.db.db_query import dbq as db
from crontabs.db.schemas import CustomerPromo
from crontabs.lib.mail import render_body_new_customer_coupon


@pytest.mark.asyncio
async def test_tmpl() -> None:
    for lang in ["en", "es", "fr", "it", "jp", "nl", "pl", "pt", "ru", "tr", "zh"]:
        body = await render_body_new_customer_coupon(
            lang, settings.TEST_EMAIL
        )
        assert f"https://whoer.net/{lang}/unsubscribe" in body \
            or "https://whoer.net/unsubscribe" in body
        assert "<!DOCTYPE html PUBLIC" in body
        print("is in", "<!DOCTYPE html PUBLIC" in body, lang)


@pytest.mark.asyncio
async def test_get_user(ins_del_user_nc_coupon: None) -> None:
    result = await db.get_customer_coupon_db()
    assert type(result) is list
    assert len(result) > 0
    assert type(result[0]) is CustomerPromo
    assert result[0].address == settings.TEST_EMAIL
