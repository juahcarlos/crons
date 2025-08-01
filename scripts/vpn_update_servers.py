import argparse
import asyncio
import json
import os
import requests
import ssl

from typing import List

from datetime import datetime

from urllib3.exceptions import InsecureRequestWarning

from config import settings
from dbm.schemas import UserId
from libs.logs import log
from crontabs.db.db_query import dbq as db
from crontabs.parser_args import get_args


requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


def usage():
    print("""
        --all or --email options is required!
        
        Usage: $0 [--server=XX] ([--email=XXX] | [--all]) [--skip-trial-com-users]
        [--daemon] ([--pid=XXX] | [--no-pid]) [--verbose] [--help]
    """)

async def get_users(args: argparse.Namespace) -> List[UserId]:
    users = []

    if args.all and args.skip_trial_com_users:
        users = await db.get_not_trial_users_db()
    elif args.all:
        users = await db.get_all_users_db()
    elif args.email is not None:
        user = await db.get_user_db(args.email)
        if user:
            log.debug(f"user.email {user.email}")
            users.append(user)
        else:
            log.error(f"There is no user in the database with email {args.email}")
            exit(0)
    else:
        usage()

    return users


async def get_servers() -> dict:
    servers = {}
    servers_db = await db.get_servers_db(settings.PROD)

    for s in servers_db:
        servers[s.server] = s.__dict__
        servers[s.server]["manage"] = {
            "url":f"https://{s.server}v.secwhapi.net:55555",
            "key": "secretauthkeywithnodoubts",
        }

    return servers


async def get_json_data(users: List[UserId]) -> List[List[str]]:
    json_data = [[], []]
    log.debug(f"00000000000000 get_json_data users {users}")
    for trial_mode in [0, 1]:

        data = {}
        size = 0

        for user in users:
            log.debug(f"00000000000000 get_json_data user.trial {user.trial} trial_mode {trial_mode}")
            if user.trial != trial_mode:
                continue

            log.debug(f"00000000000000 get_json_data trial_mode {trial_mode} user {user}")

            data[user.cn] = {
                "expires": user.expires,
                "password": user.password,
            }

            size += 1

            if size >= 20000:
                json_data[trial_mode].append(json.dumps(data))
                data = {}
                size = 0

        if size > 0:
            json_data[trial_mode].append(json.dumps(data))
            data = {}

    return json_data


async def post_update(data: List[str], server: dict) -> int:
    update_res = requests.post(
        f'{server["manage"]["url"]}/update',
        params={"auth": server["manage"]["key"]},
        data=data,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/json",
        },
        timeout=5,
        verify=False,
    )

    return update_res


async def post_ips(server: dict) -> int:
    serv = server[list(server.keys())[0]]

    print(f"serv {serv}")

    ips = serv["remote_ips"]

    log.debug(f"ips {ips}")

    ips_res = None
    try:
        ips_res = requests.post(
            f'{serv["manage"]["url"]}/ips',
            params={"auth": serv["manage"]["key"]},
            data=ips,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Content-Type": "application/json",
            },
            timeout=5,
            verify=False,
        )
    except Exception as ex:
        log.debug(f"\n\n cant connect ips to url {serv['manage']['url']} ex {ex} \n\n")

    return ips_res


async def upd(args: argparse.Namespace) -> None:
    users = await get_users(args)
    servers = await get_servers()
    json_data = await get_json_data(users)

    for trial_mode in [0, 1]:

        if settings.PROD != 1:
            if trial_mode == 1:
                continue

        for serv in servers.keys():
            server = servers[serv]

            if "trial" not in server.keys():
                server["trial"] = 0

            if int(server["trial"]) != trial_mode:
                log.debug("CONTINUEEEEEEEEEEEEEEEEEEEE")
                continue

            part = 0
            total_parts = len(json_data[trial_mode])

            for data in json_data[trial_mode]:
                part += 1

                log.debug(f"""++++++++++++++++++Send /update request to server {server} (trial={trial_mode}) 
                (partition: {part}). Request size: {len(data)}, data type {type(data)}""")

                update_res = await post_update( data[0], server)

                if str(update_res.status_code).startswith("2"):
                    log.debug(
                        f"Request /update to {server} (trial={trial_mode}) (partition: {part} of {total_parts}, {int(100.0 * part / total_parts)} successed. Body: {update_res.content.decode('utf-8')}")
                else:
                    log.debug(
                        f"Request /update to {server} (trial={trial_mode}) (partition: {part} of {total_parts}, {int(100.0 * part / total_parts)} failed. Status: {update_res.status_code}")
                return update_res.status_code

            # --- /ips EP on wman
            ips_res = await post_ips(server)

            if str(ips_res.status_code).startswith("2"):
                log.debug(
                    f"Request /ips to {server['manage']['url']} (trial={trial_mode}) successed. Status: {ips_res.status_code} Body: {ips_res.content}")
            else:
                log.debug(
                    f"Request /ips to {server['manage']['url']} (trial={trial_mode}) failed. Status: {ips_res.status_code}")


log.debug(f"----------- RUN")

async def start() -> None:
    args = get_args()

    if args.verbose:
        log.setLevel("DEBUG")
    else:
        log.setLevel("INFO")

    log.info("log.info")
    log.debug("log.debug")

    log.debug("-------------- usage ")


    if args.daemon:
        processid = os.fork()
        log.debug(f"processid {processid}")

        if processid == 0:
            await upd(args)

    else:
        await upd(args)

if __name__ == "__main__":
    asyncio.run(start())