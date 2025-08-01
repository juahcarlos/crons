import argparse
import asyncio
import getopt
import hashlib
import json
import os
import sys

from datetime import datetime
from pathlib import Path
from typing import List

sys.path.append(str(Path(__file__).parents[0]))

import pidfile
import time

from jinja2 import Environment, FileSystemLoader

from crontabs.config_cron import settings
from libs.logs import log
from libs.send_mail import SendMail
from libs.utils import generate_coupon_db

from crontabs.db.db_query import dbq
from crontabs.db.schemas import ReminderArgs, UserReminder
from crontabs.lib.utils import get_emails, get_users, langs, render_tmpl
from crontabs.lib.mail import send_all_reminder


parser = argparse.ArgumentParser()
parser.add_argument("-t", "--try-one-email", help="try-one-email")
parser.add_argument("-p", "--pid", help="pid")
parser.add_argument("-np", "--no-pid", action="store_true", help="no-pid")
parser.add_argument("-nu", "--no-unsubscribe", action="store_true", help="no-unsubscribe")

args = parser.parse_args()
pid_file = args.pid or settings.PIDFILE_REMINDER

log.debug(f"pid_file {pid_file}")


def get_args() -> ReminderArgs:
    return ReminderArgs(
        try_one_email = args.try_one_email,
        no_unsubscribe = args.no_unsubscribe,
    )


async def remind() -> List[str|None]:
    args_data = get_args()
    emails = await get_emails(args_data.try_one_email)
    users = await get_users(emails, args_data.no_unsubscribe)
    log.debug(f"emails {emails}")
    res = await send_all_reminder(users)
    return res


try:
    with pidfile.PIDFile(pid_file):
        log.debug("Process started")
        res = asyncio.run(remind())
        log.debug(f"reminder res {res}")
        error = [r for r in res if r[0] != "" and r[0] is not None]

        if error is not None and error != []:
            er = [str(e) for e in error]
            err = '\n'.join(er)
            log.error(f"ERROR vpn reminder {type(err)} {err}")
except pidfile.AlreadyRunningError:
    log.error("Already running")

log.info("Exiting")


