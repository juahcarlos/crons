import asyncio
import json
import re
import requests
import ssl
from urllib3.exceptions import InsecureRequestWarning

from config import settings
from dateutil.relativedelta import relativedelta
from libs.logs import log
from crontabs.db.db_query import dbq as db
from crontabs.db.schemas import VpnStat
from crontabs.parser_args import get_args

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


def usage() -> None:
    print("Usage: [--total] [--year] [--month] ([--pid=XXX] | [--no-pid]) [--verbose] [--help]")
    exit(0)


async def get_stat() -> VpnStat:
    servers_db = await db.get_servers_db(settings.PROD)
    print("servers_db", servers_db)

    hubname = "default"
    req_id = 1
    log.debug(f"\n\n get_stat servers_db {servers_db} \n\n")

    for serv in servers_db:
        log.debug(f"\n\n serv {serv.server} \n\n")
        url = f"https://{serv.server}v.secwhapi.net:55555"
        key = "secretauthkeywithnodoubts"

        version = requests.get(
            f"{url}/version",
            params={"auth":key},
            headers={"User-Agent":"Mozilla/5.0"},
            verify=False,
            timeout=30
        ).text

        log.debug(f"\n version {version} \n")

        stat = {}

        log.debug(f" --------- online_and_bw --------- ")
        stat = requests.get(
            f"{url}/online_and_bw/json",
            params={"auth": key},
            headers={"User-Agent":"Mozilla/5.0"},
            verify=False,
            timeout=30,
        ).json()

        if serv.softether == 1  or serv.sstp == 1 or serv.l2tp:
            log.debug(f" --------- softether --------- ")
            req_id += 1
            req = {
                "jsonrpc": "2.0",
                "id": str(req_id),
                "method": "EnumSession",
                "params": {"HubName_str": hubname},
            }

            stat_res = requests.post(
                f"{url}/softether/rpc",
                params={"auth": key},
                data=json.dumps(req),
                headers={
                    "User-Agent": "Mozilla/5.0",
                    "Content-Type": "application/json",
                },
                verify=False,
                timeout = 30,
            )
            log.debug(f"stat_res status_code {stat_res.status_code}")
            
            if str(stat_res.status_code).startswith("2"):
                stat_soft =  stat_res.json()
                stat["online_l2tp"] = 0
                stat["online_sstp"] = 0
                stat["online_softether_native"] = 0
                for session in stat_soft["result"]["SessionList"]:
                    if session["Username_str"] == "Local Bridge":
                        continue
                    log.debug(f"---- session ----")
                    log.debug(f"session type {type(session)}")
                    log.debug(f"session[Name_str] {session['Name_str']}")
                    if "[L2TP]" in session["Name_str"]:
                        stat["online_l2tp"]  += 1
                    if "[SSTP]" in session["Name_str"]:
                        stat["online_sstp"]  += 1
                    native = re.search(r"\[[\w+\d+]+\]\-", session["Name_str"])
                    if not native:
                        log.debug(f"native {native}")
                        stat["online_softether_native"]  += 1

                log.debug(f"\n\n stat {stat}")
            log.debug(f"stat_soft {stat}")

        data = VpnStat(
            server=serv.server + 'v',
            # created=datetime.now(),
            online_vpn=stat["users"]["openvpn"],
            online_proxy=stat["users"]["proxy"],
            traf_today=int(stat["traffic"]["today"]),
            traf_yesterday=int(stat["traffic"]["yesterday"]),
            traf_month=int(stat["traffic"]["month"]),
            online_sstp=stat.get("online_sstp"),
            online_l2tp=stat.get("online_l2tp"),
            online_softether_native=stat.get("online_softether_native"),
            bandwidth_today=str(stat["speed"]["today"]),
            bandwidth_yesterday=str(stat["speed"]["yesterday"]),
            bandwidth_month=str(stat["speed"]["month"]),
            wman_version=version,  
        )

        log.debug(f" --------- data {data} --------- ")

        await db.db_vpn_stat(data)
        return data


async def start() -> None:
    args = get_args()

    if args.help or (not args.total and not args.year and not args.month):
        usage()

    pid_file = args.pid or settings.PIDFILE_REMINDER

    try:
        with pidfile.PIDFile(f'/whoer/crontabs/PID/{pid_file}'):
            res = asyncio.run(get_stat())
            if res:
                log.debug(f"update res {res}")
                error = [r for r in res if r[0] != ""]

                if len(error) > 0:
                    err = '\n'.join(error)
                    log.debug(f"ERROR vpn update {err}")
    except pidfile.AlreadyRunningError:
        log.error("Already running")


if __name__ == "__main__":
    asyncio.run(start())




