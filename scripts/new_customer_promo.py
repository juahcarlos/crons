import asyncio

from typing import List

from libs.logs import log
from crontabs.db.db_query import dbq as db
from crontabs.lib.mail import send_all_new_customer_promo


async def promo() -> List[str|None]:
    log.debug("new_customer_promo send_all")
    users = await db.get_customer_promo_db()
    log.debug(f"users {users}")
    res = await send_all_new_customer_promo(users)
    return res

asyncio.run(promo())

