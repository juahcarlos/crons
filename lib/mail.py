from datetime import datetime
from typing import List

from config import settings
from libs.send_mail import Send
from libs.utils import generate_coupon_db, render_tmpl
from crontabs.db.schemas import UserId
from crontabs.lib.utils import langs
from crontabs.db.db_query import dbq


# ------ reminder

async def render_body_reminder(user: UserId) -> str:
    lang = user.lang
    email = user.email
    data_tmpl = {
            "header_notice_expired": langs[f"email.reminder-new.header-notice-expired-{lang}"],
            "email_reminder_new_herd": langs[f"email.reminder-new.herd-{lang}"],
            "email_reminder_new_herd_discount": langs[f"email.reminder-new.herd-discount-{lang}"],
            "email_reminder_new_promocode": langs[f"email.reminder-new.promocode-{lang}"],
            "email_reminder_new_promocode_valid": langs[
                f"email.reminder-new.promocode-valid-{lang}"
            ],
            "email_reminder_new_use_safety": langs[f"email.reminder-new.use-safety-{lang}"],
            "email_reminder_new_buy_vpn": langs[f"email.reminder.buy-vpn-{lang}"],

            "email_reminder_new_support": langs[f"email.reminder-new.support-{lang}"],
            "email_reminder_new_support_chat": langs[f"email.reminder-new.support-chat-{lang}"],
            "email_reminder_new_support_email": langs[f"email.reminder-new.support-email-{lang}"],
            "email_reminder_new_unsubscribe": langs[f"email.reminder-new.unsubscribe-{lang}"],
            "email_reminder_new_unsubscribe_here": langs[
                f"email.reminder-new.unsubscribe-here-{lang}"
            ],
            "email.reminder_new_sincerely": langs[f"email.reminder-new.sincerely-{lang}"],

            "link_lang": lang + "/" if lang != "en" else "",
            "email": email,
            "unsubscribe_token": settings.UNSUBSCRIBE_SECRET,
            "localtime": datetime.now().strftime("%Y"),
    }

    now_unix = int((datetime.now().strftime("%s")))
    if now_unix - user.expires > 0:
        coupon = await generate_coupon_db(dbq, 10, 30)
        data_tmpl["coupon"] = coupon.coupon

    return render_tmpl(
        "reminder_new.html",
        data_tmpl,
    )


async def render_body_new_customer_promo(lang: str, email: str) -> str:
    coupon = await generate_coupon_db(dbq, 35, 1, "180,360")
    return render_tmpl(
        f"email/newcustomer_promo_{lang}.html",
        {
            "coupon": coupon.coupon,
            "localtime": datetime.now().strftime("%Y"),
        }
    )


async def render_body_new_customer_coupon(lang: str, email) -> str:
    coupon = await generate_coupon_db(dbq, 35, 1, "180,360")
    return render_tmpl(
        f"email/newcustomer_coupon_{lang}.html",
        {
            "coupon": coupon.coupon,
            "localtime": datetime.now().strftime("%Y"),
        }
    )


async def send_one(email: str, body: str, subject: str) -> List[str | None]:
    sender = Send()
    sent = await sender.send(email, body, subject)
    sent = list(sent)
    sent.append(email)
    return sent


async def send_all_reminder(users: List[UserId]) -> List[str | None]:
    res = []

    for user in users:
        subject = langs[f"email.subjects.reminder-{user.lang}"]
        body = await render_body_reminder(user)
        sent = await send_one(user.email, body, subject)
        res.append(sent)

    return res


async def send_all_new_customer_promo(users: List[UserId]) -> List[str | None]:
    res = []

    for user in users:
        subject = langs[f"newcustomer_promo-{user.lang}"]
        body = await render_body_new_customer_promo(user.lang, user.address)
        sent = await send_one(user.address, body, subject)
        res.append(sent)

    return res


async def send_all_new_customer_coupon(users: List[UserId]) -> List[str | None]:
    res = []

    for user in users:
        subject = langs[f"newcustomer_coupon-{user.lang}"]
        body = await render_body_new_customer_coupon(user.lang, user.address)
        sent = await send_one(user.address, body, subject)
        res.append(sent)

    return res
