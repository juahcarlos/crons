import argparse
import asyncio
import copy
import pidfile

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from config import settings
from libs.logs import log
from crontabs.db.db_query import dbq as db
from crontabs.db.schemas import ChurnRate
from crontabs.parser_args import get_args_churn


def usage() -> None:
    print("Usage: [--total] [--year] [--month] ([--pid=XXX] | [--no-pid]) [--verbose] [--help]")
    exit(0)


async def process_year_stat(year: int) -> ChurnRate:
    dt1 = datetime.strptime(
        "2016-01-01 00:00:00",
        "%Y-%m-%d %H:%M:%S"
    ) - relativedelta(years=-1)

    dt2 = copy.deepcopy(dt1)
    dt2 = dt2 + relativedelta(years=+1) 

    dt3 = copy.deepcopy(dt2)
    dt3 = dt3 + relativedelta(years=+1) 

    users_in_end_of_prev_period = await db.users_in_end_of_period(dt2)
    users_new_current_period = await db.new_users_in_period(dt2, dt3)
    users_in_end_of_current_period = await db.users_in_end_of_period(dt3)

    churn_rate = round(
        (
            100.0*(
                users_in_end_of_prev_period \
                + users_new_current_period \
                - users_in_end_of_current_period
            ) / users_in_end_of_prev_period), 2
        ) if users_in_end_of_prev_period else 0

    id = await db.get_stat_churn_rate(year=year, month=None)

    data = ChurnRate(
        users_in_end_of_prev_period=users_in_end_of_prev_period,
        users_new_current_period=users_new_current_period,
        users_in_end_of_current_period=users_in_end_of_current_period,
        churn_rate=churn_rate,
    )

    if id:
        await db.update_churn_rate(data, id)
    else:
        data.year = year
        await db.insert_churn_rate(data)

    return data


async def process_month_stat(year: int, month: int) -> ChurnRate:
    dt1 = datetime.strptime(
        datetime.now().strftime("%Y-%m") + "-01 00:00:00", 
        "%Y-%m-%d %H:%M:%S"
    ) + relativedelta(months=-1)

    dt2 = copy.deepcopy(dt1)
    dt2 = dt2 + relativedelta(months=+1) 

    dt3 = copy.deepcopy(dt2)
    dt3 = dt3 + relativedelta(months=+1) 

    print("dt1", dt1, "\n")
    print("dt2", dt2, "\n")
    print("dt3", dt3, "\n")

    users_in_end_of_prev_period = await db.users_in_end_of_period(dt2)
    users_new_current_period = await db.new_users_in_period(dt2, dt3)
    users_in_end_of_current_period = await db.users_in_end_of_period(dt3)

    churn_rate = round(
        (
            100.0*(
                users_in_end_of_prev_period \
                + users_new_current_period \
                - users_in_end_of_current_period
            ) / users_in_end_of_prev_period), 2
        ) if users_in_end_of_prev_period else 0

    id = await db.get_stat_churn_rate(year=year, month=month)

    data = ChurnRate(
        users_in_end_of_prev_period=users_in_end_of_prev_period,
        users_new_current_period=users_new_current_period,
        users_in_end_of_current_period=users_in_end_of_current_period,
        churn_rate=churn_rate,
    )

    if id:
        await db.update_churn_rate(data, id)
    else:
        data.year = year
        await db.insert_churn_rate(data)

    return data


def ym(date_obj: datetime) -> int:
    return int(str(date_obj.year) + date_obj.strftime("%m"))


async def update() -> None:
    if args.total:
        log.debug("Process total stat")
        date = datetime.strptime(
            datetime.now().strftime("%Y-%m-%d") + " 00:00:00", 
            "%Y-%m-%d %H:%M:%S"
        )

        for year in range(2016, int(date.strftime("%Y"))):
            await process_year_stat(year)

        
        date = date.replace(year=2016, month=1)

        now = datetime.strptime(
            datetime.now().strftime("%Y-%m") + "-01 00:00:00", 
            "%Y-%m-%d %H:%M:%S"
        )
        
        date_ym = ym(date)
        now_ym = ym(now)
        
        while True:
            date = date + relativedelta(months=+1)
            date_ym = ym(date)
            if date_ym < now_ym:
                await process_month_stat(date.year, date.month)
            else:
                break

    elif args.year:
        log.debug("Process year stat")
        await process_year_stat(datetime.now().year - 1)

    elif args.month:
        log.debug("Process month stat")
        await process_month_stat(datetime.now().year, datetime.now().month)


async def start() -> None:
    args = get_args_churn()

    if args.help or (not args.total and not args.year and not args.month):
        usage()

    pid_file = args.pid or settings.PIDFILE_REMINDER

    try:
        with pidfile.PIDFile(f'/whoer/crontabs/PID/{pid_file}'):
            res = asyncio.run(update())
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

