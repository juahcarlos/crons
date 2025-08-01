import asyncio
import sys

from datetime import datetime
from pathlib import Path
from typing import List

sys.path.append(str(Path(__file__).parents[0]))

from crontabs.lib.utils import get_unsubscribe_token
from libs.logs import log
from libs.send_mail import Send
from crontabs.db.db_query import dbq
from libs.utils import render_tmpl, subjs


async def send_all() -> List[str|None]:
    tobuy = await dbq.lookingtobuy()

    log.debug(f"------- tobuy {tobuy} -------")
    subjects = subjs()

    res = []

    for user in tobuy:
        log.debug(f"-- user -- {user}")
        log.debug(f"------- subjects {type(subjects)} {subjects} -------")
        subject = subjects.get(f"lookingtobuy-{user.lang}")

        ltb = f"lookingtobuy_{user.lang}"

        mail_icons_x = "WhoerNet";
        mail_icons_play_google = "en_EN";
        mail_icons_apple_app = "whox-secure-vpn-without-logs/id6476266235";

        if user.lang == 'ru':
            mail_icons_x = "RuWhoer";
            mail_icons_play_google = "ru_RU";
            mail_icons_apple_app = "whox-%D0%B0%D0%BD%D0%BE%D0%BD%D0%B8%D0%BC%D0%B0%D0%B9%D0%B7%D0%B5%D1%80-%D0%B8-%D0%B7%D0%B0%D1%89%D0%B8%D1%82%D0%B0-ip/id6476266235";

        body = render_tmpl(
            f"email/{ltb}.html",
            {
                'localtime': datetime.now().strftime("%Y"),
                "mail_icons_x": mail_icons_x,
                "mail_icons_play_google": mail_icons_play_google,
                "mail_icons_apple_app": mail_icons_apple_app,
                "email": user.address,
                "unsubscribe_token": get_unsubscribe_token(user.address),
            },
        )

        sender = Send()
        sent = await sender.send(user.address, body, subject)
        log.debug(f"-- sent -- {sent}", )
        res.append(sent)

    return res

asyncio.run(send_all())

