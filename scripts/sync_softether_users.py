#########
# collect enabled servers with sstp and no trial
# if user -
#   check if user is paid,
#   loop servers:
#       call_rpc create
# else -
#   collect all paid users
#   loop all servers
#
#
#
#
#########
import argparse
import asyncio
import json
import requests
import os

from typing import List
from urllib3.exceptions import InsecureRequestWarning

from dbm.schemas import UserId
from libs.logs import log
from libs.servers_update import servers_update
from crontabs.db.db_query import dbq as db
from crontabs.parser_args import get_args


requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


async def sync_softether(users: List[UserId], server: str|None) -> List[UserId]:
    log.debug(f"start soft_sync process")
    data = {}

    for user in users:
        row = {"expires": user.expires, "password": user.password}
        # log.debug(f"row {row}")
        data[user.cn] = row

    try:
        await servers_update(db, json.dumps(data), server)
    except Exception as ex:
        log.error(f"can't sync_softether ex={ex}")


async def get_users(args: argparse.Namespace) -> List[UserId]:
    users = []
    if args.user:
        user = await db.get_user_by_email(args.user)
        if user is not None:
            if user.trial == 0:
                users.append(user)
            else:
                print(f"User {args.user} is trial, couldn't update softerther")
                exit(0)
        else:
            print(f"User {args.user} not in DB")
            exit(0)
    else:
        users_ = await db.get_not_trial_users_db()
        if users_ is not None:
            if len.users_ == 0:
                print(f"Users DB request is empty, couldn't update softerther")
                exit(0)
            users.extend(users_)
    return users


async def sync(args: argparse.Namespace) -> None:
    users = await get_users(args)
    await sync_softether(users)


async def start() -> None:
    args = get_args()

    if args.verbose:
        log.setLevel("DEBUG")
    else:
        log.setLevel("INFO")

    if args.daemon:
        processid = os.fork()
        log.debug(f"processid {processid}")

        if processid == 0:
            await sync(args)

    else:
        await sync(args)


if __name__ == "__main__":
    asyncio.run(start())



