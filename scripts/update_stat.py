import asyncio
import json

import pidfile

import argparse

from datetime import datetime, timedelta
from typing import Any, List, Tuple

from crontabs.config_cron import settings
from crontabs.db.db_query import dbq as db
from crontabs.db.schemas import (
    PlanCount,
    UserDateCount,
    TransDateCount,
    TransDateDaysCount,
)
from libs.logs import log
from crontabs.parser_args import get_args_update_stat


def usage():
    # print("Usage: [--total] [--today] [--yesterday] [--date=YYYY-MM-DD] [--one-processor ...] ([--pid=XXX] | [--no-pid]) [--verbose] [--help]")
    exit(0)


async def get_metric(alias: str) -> int:
    metric_id = await db.get_stat_metrics_id(alias) # 'stat_metrics', 'id', {alias = > $alias})->list;
    if metric_id is None:
        name = alias
        name = name.capitalize()
        name = name.replace("_", " ")
        metric_id = await db.insert_metric(alias, name)
    return metric_id


class Update:
    def __init__(self, args: argparse.Namespace, arg_date: str, next_date: str):
        self.args = args
        self.arg_date = arg_date
        self.next_date = next_date


    async def update_all_registered_users(self) -> Tuple[int, int]:
        log.debug("all_registered_users")

        metric_id = await get_metric('all_registered_users')
        log.debug(f"--------- metric_id {metric_id}")

        value = await db.get_all_users_count()
        log.debug(f"count = {value}")

        await db.upsert_stat(metric_id, value)

        log.debug("Done")
        return metric_id, value


    async def update_all_active_paid_users(self) -> Tuple[int, int]:
        log.debug("all_active_paid_users")

        metric_id = await get_metric('all_active_paid_users')
        log.debug(f"----- metric_id {metric_id}")
        value = await db.get_all_active_paid_users()

        await db.upsert_stat(metric_id, value)
        log.debug("Done")
        return metric_id, value


    async def update_all_active_paid_users_by_plans(self) -> Tuple[int, PlanCount]:
        log.debug("all_active_paid_users_by_plans")

        stats = await db.all_active_paid_users_by_plans()
        other = 0

        for stat in stats:
            if stat.plan not in (30, 180, 360):
                other += stat.count

        stats.append(PlanCount(plan="other", count=other ))

        for stat in (stats):
            metric_id = await get_metric(f"all_active_paid_users_by_plan_{stat.plan}")
            log.debug(f"metric_id {metric_id}")
            await db.upsert_stat(metric_id, stat.count)

        log.debug("Done")
        return metric_id, stats


    async def update_all_active_free_users(self) -> Tuple[int, int]:
        log.debug("all_active_free_users")
        metric_id = await get_metric("all_active_free_users")
        value = await db.get_all_active_free_users()

        await db.upsert_stat(metric_id, value)
        log.debug("Done")
        return metric_id, value


    async def update_online_users(self) -> Tuple[int, int]:
        log.debug("online_users")
        metric_id = await get_metric('online_users')

        servers_ = await db.get_servers_enabled()
        servers = [r.server for r in servers_]

        value = 0
        for srv in servers:
            result = await db.get_vpn_stat(srv)
            if result is None:
                continue
            value += result.online_vpn
            value += result.online_proxy

        await db.upsert_stat(metric_id, value)
        log.debug("Done")
        return metric_id, value


    async def update_paid_user_countries(self) -> Tuple[int, str]:
        log.debug("paid_user_countries")
        metric_id = await get_metric('paid_user_countries')
        ext_ = await db.get_paid_user_countries()
        ext = json.dumps([e.model_dump() for e in ext_])

        await db.upsert_stat(metric_id, None, ext)
        log.debug("Done")
        return metric_id, ext


    async def update_trial_user_countries_wo_extension(self) -> Tuple[int, str]:
        log.debug("trial_user_countries_wo_extension")
        metric_id = await get_metric('trial_user_countries_wo_extension')
        ext_ = await db.get_trial_user_countries_wo_extension()
        ext = json.dumps([e.model_dump() for e in ext_])

        await db.upsert_stat(metric_id, None, ext)
        log.debug("Done")
        return metric_id, ext


    async def update_trial_user_countries_extension_only(self) -> Tuple[int, str]:
        log.debug("trial_user_countries_extension_only")
        metric_id = await get_metric('trial_user_countries_extension_only')
        ext_ = await db.get_trial_user_countries_extension_only()
        log.debug(f"-------- ext_ {ext_}")
        ext = json.dumps([e.model_dump() for e in ext_])

        await db.upsert_stat(metric_id, None, ext)
        log.debug("Done")
        return metric_id, ext


    async def update_registrations(self) -> Tuple[int, List[UserDateCount]]:
        log.debug("registrations")
        metric_id = await get_metric('registrations')
        data = await db.get_registrations()

        for row in data:
            log.debug(f"metric_id {metric_id} date {type(row.date)} {row.date} value {row.value}")
            await db.upsert_stat(metric_id, row.value, None, row.date.date())

        log.debug("Done")
        return metric_id, data


    async def update_trial_registrations_wo_extension_count(self) -> Tuple[int, List[UserDateCount]]:
        log.debug("trial_registrations_wo_extension_count")

        metric_id = await get_metric('trial_registrations_wo_extension_count')
        data = await db.get_registrations_wo_extension_count(self.arg_date, self.next_date)

        for row in data:
            log.debug(f"metric_id {metric_id} date {type(row.date)} {row.date} value {row.value}")
            await db.upsert_stat(metric_id, row.value, None, row.date.date())

        log.debug("Done")
        return metric_id, data


    async def update_trial_registrations_extension_only_count(self) -> Tuple[int, List[UserDateCount]]:
        log.debug("trial_registrations_extension_only_count")
        metric_id = await get_metric('trial_registrations_extension_only_count')
        data = await db.get_trial_registrations_extension_only_count(self.arg_date, self.next_date)

        for row in data:
            log.debug(f"metric_id {metric_id} date {type(row.date)} {row.date} cvalue {row.cvalue}")
            await db.upsert_stat(metric_id, row.cvalue, None, row.date)

        log.debug("Done")
        return metric_id, data


    async def update_payments_amount(self) -> Tuple[int, dict]:
        log.debug("payments_amount")
        metric_id = await get_metric('payments_amount')
        data = await db.get_payments_amount(self.arg_date, self.next_date)

        data_dict = {}

        for row in data:
            date = row.date
            system = row.system
            sum_value = row.sum
            if date not in data_dict:
                data_dict[date] = {}
            data_dict[date][system] = sum_value

        for date in sorted(data_dict.keys()):
            ext = json.dumps(data_dict[date])
            total_sum = sum(data_dict[date].values())
            log.debug(f"JSON for {date}: {ext}")
            log.debug(f"Total sum for {date}: {total_sum}")
            await db.upsert_stat(metric_id, total_sum, ext, date)

        log.debug("Done")
        return metric_id, data_dict


    async def update_premium_payments_count(self) -> Tuple[int, List[TransDateCount]]:
        log.debug("premium_payments_count")
        metric_id = await get_metric('premium_payments_count')
        data = await db.get_premium_payments_count(self.arg_date, self.next_date)

        for row in data:
            log.debug(f"metric_id {metric_id} date {type(row)} {row}")
            await db.upsert_stat(metric_id, row.count, None, row.date)

        log.debug("Done")
        return metric_id, data


    async def update_trial_payments_wo_extension_count(self) -> Tuple[int, List[TransDateCount]]:
        log.debug("trial_payments_wo_extension_count")
        metric_id = await get_metric('payments_wo_extension_count')
        data = await db.get_payments_wo_extension_count(self.arg_date, self.next_date)

        for row in data:
            log.debug(f"metric_id {metric_id} date {type(row)} {row}")
            await db.upsert_stat(metric_id, row.count, None, row.date)

        log.debug("Done")
        return metric_id, data


    async def update_trial_payments_extension_only_count(self) -> Tuple[int, List[TransDateCount]]:
        log.debug("trial_payments_extension_only_count")
        metric_id = await get_metric('trial_payments_extension_only_count')
        data = await db.get_trial_payments_extension_only_count(self.arg_date, self.next_date)

        for row in data:
            log.debug(f"metric_id {metric_id} date {type(row)} {row}")
            await db.upsert_stat(metric_id, row.count, None, row.date)

        log.debug("Done")
        return metric_id, data


    async def update_payments_by_plan(self) -> Tuple[int, List[TransDateDaysCount]]:
        log.debug("payments_by_plan")

        metric_id = await get_metric('payments_by_plan')
        data = await db.get_payments_by_plan(self.arg_date, self.next_date)

        data_dict = {}

        for row in data:
            date = row.date
            count = row.count
            if date not in data_dict.keys():
                data_dict[date] = {}
            if "total" not in data_dict[date].keys():
                data_dict[date]["total"] = 0
            data_dict[date]["total"] += count
            if "plans" not in data_dict[date].keys():
                data_dict[date]["plans"] = {}
            data_dict[date]["plans"][row.days] = count

        for date in sorted(data_dict.keys()):
            ext = json.dumps(data_dict[date]["plans"])
            total_sum = data_dict[date]["total"]
            await db.upsert_stat(metric_id, total_sum, ext, date)

        log.debug("Done")
        return metric_id, data

    async def update_outcoming_users(self) -> Tuple[dict, dict]:
        log.debug("outcoming_users")

        data = await db.get_outcoming_users(self.arg_date, self.next_date)

        metrics_dict = {}
        data_dict = {}

        for row in data:
            date = row.date
            count = row.count
            if date not in data_dict.keys():
                data_dict[date] = {}
            data_dict[date]["plan"] = count

            log.debug(f"data_dict {data_dict}")

        for date in sorted(data_dict.keys()):
            for plan in (30, 180, 360, "other"):
                metric_id = await get_metric(f'outcoming_users_{plan}')
                total_sum = data_dict[date]["plan"]
                log.debug(f"Total sum for {date}: {total_sum} metric_id={metric_id}")
                metrics_dict[plan] = metric_id
                await db.upsert_stat(metric_id, total_sum, None, date)

        log.debug("Done")
        return metrics_dict, data_dict


    async def update_renewed_users(self) -> Tuple[int, List[TransDateCount]]:
        log.debug("renewed_users")

        metric_id = await get_metric('renewed_users')
        data = await db.get_renewed_users(self.arg_date, self.next_date)

        for row in data:
            await db.upsert_stat(metric_id, row.count, None, row.date)

        log.debug("Done")
        return metric_id, data


async def execute(update, method_name: str, args) -> Tuple[int, Any]:
    obj = Update(args)
    method = getattr(obj, method_name, None)
    return await method(update)


async def run(args, arg_date, next_date) -> None:
    update = Update(args, arg_date, next_date)
    if args.one_processor is not None:
        cls = args.one_processor
        await execute(update, cls, args)
    else:
        clslist = [cls for cls in dir(Update) if cls.startswith("update_")]
        for cls in clslist:
            await execute(update, cls, args)


async def start() -> None:
    args = get_args_update_stat()

    if args.total is None and args.today is None \
            and args.yesterday is None and args.date is None:
        usage()

    if args.help:
        usage()

    if args.verbose:
        log.setLevel("DEBUG")
    else:
        log.setLevel("INFO")

    if args.today:
        arg_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).date().isoformat()
    elif args.yesterday:
        arg_date = (datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0,
                                                                microsecond=0).date().isoformat()

    dt = datetime.strptime(arg_date, '%Y-%m-%d')
    next_date = (dt + timedelta(days=1)).date().isoformat()

    pid_file = args.pid or settings.PIDFILE_UPDATE_STAT

    try:
        with pidfile.PIDFile(pid_file):
            asyncio.run(run(arg_date, next_date))
    except pidfile.AlreadyRunningError:
        log.error("Already running")


if __name__ == "__main__":
    asyncio.run(start())
















