import json

from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import (
    case, cast, delete, distinct, func, insert,
    Integer, or_, select, update, union
)
from sqlalchemy.orm import aliased
from sqlalchemy.sql import and_

from dbm.db_main import DbMain
from dbm.database import DbQuery as DBQ, DbQueryMixin
from libs.logs import log

from dbm.models import (
    Coupons
)
from crontabs.db.models import (
    BuyFormFilling,
    ServersConfig,
    ServersConfigDev,
    Stat,
    StatChurnRate,
    StatMetrics,
    Transactions,
    Users,
    VpnServersStat,
)
from crontabs.db.schemas import (
    BuyFormFill,
    ChurnRate,
    ChurnRateId,
    CustomerPromo,
    PlanCount,
    ServerDb,
    ServerSrv,
    StatDB,
    StatMetricsDB,
    TransCount,
    TransCountryMailCount,
    TransDateCount,
    TransDateDaysCount,
    TransDatePlanCount,
    TransPaymentAmount,
    UserDateCount,
    UserId,
    UsersDateCount,
    VpnStat,
)
from dbm.schemas import CouponsPd, UserFull


class DbQuery(DBQ, DbMain, DbQueryMixin):
    async def get_user_db(self, email: str) -> UserId:
        statement = select(Users).where(Users.email == email)
        self.data_class = UserId
        result_ = await self.result_one(statement)
        return result_

    async def get_all_users_db(self) -> List[UserId]:
        statement = select(Users)
        self.data_class = UserId
        result_ = await self.result(statement)
        return result_

    async def get_all_users_reminder(self) -> List[UserId]:
        statement = select(Users).where(
            Users.expires.between(
                int(datetime.now().strftime("%s")) - 86400 * 2,
                int(datetime.now().strftime("%s")) + 86400,
            )
        )

        self.data_class = UserId
        result_ = await self.result(statement)
        return result_

    async def get_not_trial_users_db(self) -> List[UserId]:
        statement = select(Users).where(Users.trial == 0)
        log.debug(f"statement {type(statement)} {statement}")
        self.data_class = UserId
        result_ = await self.result(statement)
        return result_

    async def get_servers_db(self, prod: int) -> List[ServerDb]:
        table = ServersConfig
        if prod != 1:
            table = ServersConfigDev
        statement = select(table).where(and_(table.enabled == 1, table.hidden == 0))
        self.data_class = ServerDb
        result_ = await self.result(statement)
        return result_

    async def get_servers_db_server(self, prod: int, server: str) -> ServerDb:
        table = ServersConfig
        if prod != 1:
            table = ServersConfigDev
        statement = select(table).where(
            and_(table.enabled == 1, table.hidden == 0, table.server == server)
        )
        self.data_class = ServerDb
        result_ = await self.result_one(statement)
        return result_

    async def lookingtobuy(self) -> List[BuyFormFill]:
        f = aliased(BuyFormFilling)
        f2 = aliased(BuyFormFilling)

        statement1 = (
            select(
                Users.email.label("address"),
                Users.lang,
                Users.id.label("users_id"),
            )
            .where(
                Users.email.in_(
                    select(Transactions.email).where(
                        and_(
                            Transactions.created.between(
                                str(datetime.now() - timedelta(hours=2)),
                                str(datetime.now() - timedelta(hours=1)),
                            ),
                            Transactions.trial.is_(False),
                            Transactions.complete.is_(False),
                        )
                    )
                )
            )
            .where(
                or_(
                    Users.expires.is_(None),
                    Users.expires < int((datetime.now() + timedelta(days=25)).strftime("%s")),
                )
            )
        )

        statement2 = (
            select(
                Users.email.label("address"),
                select(f2.lang).where(f2.email == f.email)
                .order_by(f2.created.desc()).label("lang"),
                Users.id.label("users_id"),
            )
            .where(
                f2.created.between(
                    str(datetime.now() - timedelta(hours=2)),
                    str(datetime.now() - timedelta(hours=1)),
                )
            )
            .where(f2.email is not None)
            .where(
                f2.email.notin_(
                    select(
                        Users.email
                    )
                    .where(
                        Users.email.in_(
                            select(Transactions.email)
                            .where(
                                Transactions.created.between(
                                    str(datetime.now() - timedelta(hours=2)),
                                    str(datetime.now() - timedelta(hours=1)),
                                )
                            )
                            .where(Transactions.trial.is_(False))
                            .where(Transactions.complete.is_(False))
                        )
                    )
                    .where(
                        or_(
                            Users.expires is None,
                            Users.expires < int(
                                (datetime.now() + timedelta(days=25)).strftime("%s")
                            )
                        )
                    )
                )
            )
        )
        statement = (
            union(statement1, statement2)
            .group_by(statement1.c.address)
            .group_by(statement1.c.users_id.desc())
        )
        self.data_class = BuyFormFill
        res = await self.result(statement)
        return res

    async def get_customer_promo_db(self) -> List[CustomerPromo]:
        statement = (
            select(
                Users.email.label("address"),
                Users.lang,
            )
            .where(
                Users.email.in_(
                    select(Transactions.email)
                    .with_hint(Transactions, "USE INDEX(transactions_expires)")
                    .where(
                        and_(
                            Transactions.expires.between(
                                (datetime.now() + timedelta(days=7)) - timedelta(hours=1),
                                datetime.now() + timedelta(days=7),
                            ),
                            Transactions.days == 30,
                            Transactions.trial.is_(False),
                            Transactions.complete.is_(True),
                        )
                    )
                )
            )
        )
        self.data_class = CustomerPromo
        result_ = await self.result(statement)
        return result_

    async def get_customer_coupon_db(self) -> List[CustomerPromo]:
        statement = (
            select(
                Users.email.label("address"),
                Users.lang,
            )
            .join(Transactions, Transactions.email == Users.email)
            .where(
                and_(
                    Transactions.created.between(
                        (datetime.now() - timedelta(days=1)) - timedelta(hours=1),
                        datetime.now() - timedelta(days=1),
                    ),
                    Transactions.days == 30,
                    Transactions.trial.is_(True),
                    Transactions.complete.is_(True)
                )
            )
        )
        self.data_class = CustomerPromo
        result_ = await self.result(statement)
        return result_

    async def users_in_end_of_period(self, dt: datetime) -> List[TransCount]:
        statement = select(
            func.count(distinct(Transactions.email)).label("count")
        ) \
            .where(Transactions.trial == 0) \
            .where(Transactions.complete == 1) \
            .where(Transactions.created < dt) \
            .where(Transactions.expires >= dt)
        self.data_class = TransCount
        result_ = await self.result_one(statement)
        return result_.count

    async def new_users_in_period(self, dt2: datetime, dt3: datetime) -> List[TransCount]:
        statement = select(
            func.count(distinct(Transactions.email)).label("count")
        ) \
            .where(Transactions.trial == 0) \
            .where(Transactions.complete == 1) \
            .where(Transactions.created >= dt2) \
            .where(Transactions.created < dt3) \
            .where(Users.created >= dt2) \
            .where(Users.created < dt3) \
            .join(Users, Transactions.email == Users.email)
        self.data_class = TransCount
        result_ = await self.result_one(statement)
        return result_.count

    async def get_stat_churn_rate(self, year: int, month: int) -> ChurnRateId:
        statement = select(StatChurnRate.id) \
            .where(StatChurnRate.year == year) \
            .where(StatChurnRate.month == month)
        self.data_class = ChurnRateId
        result_ = await self.result_one(statement)
        if result_ is not None:
            return result_.id

    async def get_stat_metrics_id(self, alias: str) -> StatMetricsDB:
        statement = select(StatMetrics).where(StatMetrics.alias == alias)
        self.data_class = StatMetricsDB
        result_ = await self.result_one(statement)
        return result_.id

    async def get_all_users_count(self) -> int:
        statement = select(func.count(Users.id).label("count"))
        self.data_class = TransCount
        result_ = await self.result_one(statement)
        return result_.count

    async def get_all_active_paid_users(self) -> TransCount:
        statement = (
            select(
                func.count(distinct(Users.id)).label("count")
            )
            .where(
                and_(
                    Users.trial == 0,
                    Users.expires > int(datetime.now().strftime("%s")),
                    Transactions.expires > datetime.now(),
                    Transactions.trial == 0,
                    Transactions.complete == 1,
                )
            ) .join(Transactions, Transactions.email == Users.email)
        )
        self.data_class = TransCount
        result_ = await self.result_one(statement)
        return result_.count

    async def upsert_stat(
            self,
            metric_id: int,
            value: int = None,
            ext: str = None,
            date: datetime.now().date() = None,
    ) -> None:
        stat_id = await self.get_stat(metric_id, date)
        if stat_id:
            await self.update_stat(
                stat_id, metric_id, date, value, ext=ext
            )
        else:
            await self.insert_stat(
                metric_id, date, value, ext=ext
            )

    async def get_stat(self, metric_id, date=None) -> StatDB:
        statement = select(Stat).where(Stat.metric_id == metric_id)
        if date is not None:
            statement = statement.where(Stat.date == date)
        self.data_class = StatDB
        result_ = await self.result_one(statement)
        return result_.id

    async def all_active_paid_users_by_plans(self) -> List[PlanCount]:
        statement = (
            select(
                Users.plan,
                func.count(distinct(Users.id)).label("count"),
            )
            .where(Users.trial == 0)
            .where(Users.expires > int(datetime.now().strftime("%s")))
            .group_by(Users.plan)
        )
        self.data_class = PlanCount
        result_ = await self.result(statement)
        return result_

    async def get_all_active_free_users(self) -> int:
        statement = (
            select(
                func.count(distinct(Users.id)).label("count")
            )
            .where(Users.trial == 1)
            .where(Users.expires > int(datetime.now().strftime("%s")))
        )
        self.data_class = TransCount
        result_ = await self.result_one(statement)
        return result_.count

    async def get_servers_enabled(self) -> List[ServerSrv]:
        statement = select(ServersConfig.server) \
            .where(ServersConfig.enabled == 1) \
            .where(ServersConfig.hidden == 0)
        self.data_class = ServerSrv
        result_ = await self.result(statement)
        return result_

    async def get_paid_user_countries(self) -> List[TransCountryMailCount]:
        statement = (
            select(
                Transactions.country_iso.label("country"),
                func.count(distinct(Transactions.email)).label("cvalue"),
            )
            .where(Transactions.trial == 0)
            .where(Transactions.complete == 1)
            .group_by(Transactions.country_iso)
        )
        self.data_class = TransCountryMailCount
        result_ = await self.result(statement)
        return result_

    async def get_trial_user_countries_wo_extension(self) -> List[TransCountryMailCount]:
        statement = (
            select(
                Users.country_iso.label("country"),
                func.count(Users.country_iso).label("cvalue"),
            )
            .where(Users.trial == 0)
            .where(Users.email.notlike("%@trial.com"))
            .group_by(Users.country_iso)
        )
        self.data_class = TransCountryMailCount
        result_ = await self.result(statement)
        return result_

    async def get_registrations(
        self, date: str = None, next_date: str = None
    ) -> List[UserDateCount]:
        statement = select(
            Users.created.label("date"),
            func.count(Users.id).label("value"),
        )
        if date is not None and next_date is not None:
            statement = statement.where(
                Users.created.between(
                    datetime.strptime(date, "%Y-%m-%d"),
                    datetime.strptime(next_date, "%Y-%m-%d")
                )
            )
        statement = statement.group_by(
            func.date(Users.created)
        ).order_by(
            func.date(Users.created)
        )
        self.data_class = UserDateCount
        result_ = await self.result(statement)
        return result_

    async def get_registrations_wo_extension_count(
            self, date: str = None, next_date: str = None
    ) -> List[UserDateCount]:
        statement = (
            select(
                Users.created.label("date"),
                func.count(Users.id).label("value"),
            )
            .where(Users.trial == 1)
            .where(Users.email.notlike("%@trial.com"))
        )

        if date is not None and next_date is not None:
            statement = statement.where(
                Users.created.between(
                    datetime.strptime(date, "%Y-%m-%d"),
                    datetime.strptime(next_date, "%Y-%m-%d")
                )
            )
        statement = statement.group_by(
            func.date(Users.created)
        ).order_by(
            func.date(Users.created)
        )
        self.data_class = UserDateCount
        result_ = await self.result(statement)
        return result_

    async def get_trial_registrations_extension_only_count(
            self, date: str = None, next_date: str = None
    ) -> List[UserDateCount]:
        statement = (
            select(
                func.date(Users.created).label("date"),
                func.count(Users.id).label("cvalue"),
            )
            .where(Users.trial == 1)
            .where(Users.email.like("%@trial.com"))
        )

        if date is not None and next_date is not None:
            statement = statement.where(
                Users.created.between(
                    datetime.strptime(date, "%Y-%m-%d"),
                    datetime.strptime(next_date, "%Y-%m-%d")
                )
            )
        statement = statement.group_by(Users.country_iso)
        self.data_class = UsersDateCount
        result_ = await self.result(statement)
        return result_

    async def get_payments_amount(
            self, date: str = None, next_date: str = None
    ) -> List[TransPaymentAmount]:
        system_col = Transactions.system.label("systema")
        statement = (
            select(
                func.date(Transactions.created).label("date"),
                Transactions.system,
                cast(func.sum(Transactions.amount) * 100.0, Integer).label("sum")
            )
            .where(Transactions.complete == 1)
        )

        if date is not None and next_date is not None:
            statement = statement.where(
                Transactions.created.between(
                    datetime.strptime(date, "%Y-%m-%d"),
                    datetime.strptime(next_date, "%Y-%m-%d")
                )
            )
        statement = statement.group_by(
            func.date(Transactions.created), system_col
        ).order_by(
            func.date(Transactions.created), system_col
        )
        self.data_class = TransPaymentAmount
        result_ = await self.result(statement)
        return result_

    async def get_premium_payments_count(
            self, date: str = None, next_date: str = None
    ) -> List[TransDateCount]:
        statement = (
            select(
                func.date(Transactions.created).label("date"),
                func.count(Transactions.id).label("count"),
            )
            .where(Transactions.complete == 1)
            .where(Transactions.trial == 0)
        )

        if date is not None and next_date is not None:
            statement = statement.where(
                Transactions.created.between(
                    datetime.strptime(date, "%Y-%m-%d"),
                    datetime.strptime(next_date, "%Y-%m-%d")
                )
            )
        statement = statement.group_by(
            func.date(Transactions.created)
        ).order_by(
            func.date(Transactions.created)
        )
        self.data_class = TransDateCount
        result_ = await self.result(statement)
        return result_

    async def get_payments_wo_extension_count(
            self, date: str = None, next_date: str = None
    ) -> List[TransDateCount]:
        statement = (
            select(
                func.date(Transactions.created).label("date"),
                func.count(Transactions.id).label("count"),
            )
            .where(Transactions.complete == 1)
            .where(Transactions.trial == 1)
            .where(Transactions.email.notlike("%@trial.com"))
        )

        if date is not None and next_date is not None:
            statement = statement.where(
                Transactions.created.between(
                    datetime.strptime(date, "%Y-%m-%d"),
                    datetime.strptime(next_date, "%Y-%m-%d")
                )
            )
        statement = statement.group_by(
            func.date(Transactions.created)
        ).order_by(
            func.date(Transactions.created)
        )
        self.data_class = TransDateCount
        result_ = await self.result(statement)
        return result_

    async def get_trial_payments_extension_only_count(
            self, date: str = None, next_date: str = None
    ) -> List[TransDateCount]:
        statement = (
            select(
                func.date(Transactions.created).label("date"),
                func.count(Transactions.id).label("count"),
            )
            .where(Transactions.complete == 1)
            .where(Transactions.trial == 1)
            .where(Transactions.email.like("%@trial.com"))
        )

        if date is not None and next_date is not None:
            statement = statement.where(
                Transactions.created.between(
                    datetime.strptime(date, "%Y-%m-%d"),
                    datetime.strptime(next_date, "%Y-%m-%d")
                )
            )
        statement = statement.group_by(
            func.date(Transactions.created)
        ).order_by(
            func.date(Transactions.created)
        )
        self.data_class = TransDateCount
        result_ = await self.result(statement)
        return result_

    async def get_payments_by_plan(
            self, date: str = None, next_date: str = None
    ) -> List[TransDateDaysCount]:
        statement = (
            select(
                func.date(Transactions.created).label("date"),
                Transactions.days,
                func.count(Transactions.id).label("count"),
            )
            .where(Transactions.complete == 1)
        )

        if date is not None and next_date is not None:
            statement = statement.where(
                Transactions.created.between(
                    datetime.strptime(date, "%Y-%m-%d"),
                    datetime.strptime(next_date, "%Y-%m-%d")
                )
            )
        statement = statement.group_by(
            func.date(Transactions.created)
        ).order_by(
            func.date(Transactions.created)
        )
        self.data_class = TransDateDaysCount
        result_ = await self.result(statement)
        return result_

    async def get_outcoming_users(
            self, date: str = None, next_date: str = None
    ) -> List[TransDatePlanCount]:
        t1 = aliased(Transactions)
        t2 = aliased(Transactions)

        case_ex = case(
            (t1.days.in_([30, 180, 360]), t1.days),
            else_='other'
        ).label('plan')

        subquery = select(t2.id).where(
            and_(
                t2.email == t1.email,
                t2.created >= t1.created,
                t2.created <= t1.expires,
                t2.trial == 0,
                t2.complete == 1,
                t2.id != t1.id
            )
        ).limit(1).scalar_subquery()

        statement = (
            select(
                func.date(t1.expires).label('date'),
                case_ex,
                func.count().label('count')
            ).select_from(t1)
            .where(
                and_(
                    t1.trial == 0,
                    t1.complete == 1,
                    t1.expires <= func.now(),
                    subquery.is_(None)
                )
            )
        )

        if date is not None and next_date is not None:
            statement = statement.where(
                t1.expires.between(
                    datetime.strptime(date, "%Y-%m-%d"),
                    datetime.strptime(next_date, "%Y-%m-%d")
                )
            )
        statement = statement.group_by(
            func.date(t1.expires),
            case_ex
        ).order_by(
            func.date(t1.expires),
            t1.days
        )
        self.data_class = TransDatePlanCount
        result_ = await self.result(statement)
        return result_

    async def get_renewed_users(
            self, date: str = None, next_date: str = None
    ) -> List[TransDateCount]:
        t1 = aliased(Transactions)
        t2 = aliased(Transactions)

        subquery = (
            select(t2.expires)
            .where(
                and_(
                    t2.email == t1.email,
                    t2.id != t1.id,
                    t2.created < t1.created,
                    t2.trial == 0,
                    t2.complete == 1,
                )
            )
            .order_by(t2.expires.desc())
            .limit(1).scalar_subquery()
        )

        statement = (
            select(
                func.date(t1.created).label('date'),
                func.count().label('count')
            ).select_from(t1)
            .where(
                and_(
                    t1.trial == 0,
                    t1.complete == 1,
                    subquery < t1.created
                )
            )
        )

        if date is not None and next_date is not None:
            statement = statement.where(
                t1.created.between(
                    datetime.strptime(date, "%Y-%m-%d"),
                    datetime.strptime(next_date, "%Y-%m-%d")
                )
            )
        statement = statement.group_by(
            func.date(t1.created)
        ).order_by(
            func.date(t1.created)
        )
        self.data_class = TransDateCount
        result_ = await self.result(statement)
        return result_

    async def get_trial_user_countries_extension_only(self) -> List[TransCountryMailCount]:
        statement = (
            select(
                Users.country_iso.label("country"),
                func.count(Users.country_iso).label("cvalue"),
            )
            .where(Users.trial == 1)
            .where(Users.email.like("%@trial.com"))
            .group_by(Users.country_iso)
        )
        self.data_class = TransCountryMailCount
        result_ = await self.result(statement)
        return result_

        # -------- create ---------

    async def insert_stat(
            self,
            metric_id: int,
            date: datetime.now().date() = None,
            value: Optional[int | None] = None,
            ext: Optional[str | None] = None,
    ) -> None:
        statement = insert(Stat).values(
            metric_id=metric_id,
            date=date,
            value=value,
            ext=ext,
        )
        await self.result_insert(statement)

    async def insert_metric(self, alias: str, name: str) -> int:
        statement = insert(StatMetrics).values(
            alias=alias,
            name=name,
        ).returning(StatMetrics)
        res = await self.result_insert(statement)
        result = StatMetricsDB(**json.loads(res)[0])
        return result.id

    async def db_vpn_stat(self, data: VpnStat) -> None:
        statement = insert(VpnServersStat).values(
            server=data.server,
            online_vpn=data.online_vpn,
            online_proxy=data.online_proxy,
            traf_today=data.traf_today,
            traf_yesterday=data.traf_yesterday,
            traf_month=data.traf_month,
            bandwidth_today=data.bandwidth_today,
            bandwidth_yesterday=data.bandwidth_yesterday,
            bandwidth_month=data.bandwidth_month,
            wman_version=data.wman_version,
        )
        await self.result_insert(statement)

    async def insert_user(self, user: UserFull) -> None:
        statement = insert(Users).values(
            email=user.email,
            created=user.created,
            plan=user.plan,
            dubious=user.dubious,
            subscribed=user.subscribed,
            lang=user.lang,
        )
        await self.result_insert(statement)

    async def insert_lookingtobuy(self, user: UserFull) -> None:
        statement = insert(BuyFormFilling).values(
            email=user.email,
            lang=user.lang,
        )
        await self.result_insert(statement)

    async def insert_coupon(self, data: CouponsPd) -> None:
        statement = insert(Coupons).values(
            coupon=data.coupon,
            percent=data.percent,
            created=data.created,
            expiration=data.expiration,
            plans=data.plans,
        )
        await self.result(statement)

    async def insert_churn_rate(self, data: ChurnRate) -> None:
        statement = insert(StatChurnRate).values(
            year=data.year,
            month=None,
            users_in_end_of_prev_period=data.users_in_end_of_prev_period,
            new_users_in_curr_period=data.users_new_current_period,
            users_in_end_of_curr_period=data.users_in_end_of_current_period,
            churn_rate=data.churn_rate,
        )
        await self.result_insert(statement)

    # -------- update --------

    async def update_stat(
        self,
        stat_id: int,
        metric_id: int,
        date: datetime.now().date() = None,
        value: Optional[int | None] = None,
        ext: Optional[str | None] = None,
    ) -> None:
        statement = (
            update(Stat)
            .where(Stat.id == stat_id)
            .values(
                metric_id=metric_id,
                date=date,
                value=value,
                ext=ext,
            )
        )
        await self.result(statement)

    async def update_churn_rate(self, data: ChurnRate, rate_id):
        statement = (
            update(StatChurnRate)
            .where(StatChurnRate.id == rate_id)
            .values(
                users_in_end_of_prev_period=data.users_in_end_of_prev_period,
                new_users_in_curr_period=data.users_new_current_period,
                users_in_end_of_curr_period=data.users_in_end_of_current_period,
                churn_rate=data.churn_rate,
            )
        )
        await self.result(statement)

    async def update_user_after_insert(self, user: UserId):
        statement = update(Users).where(Users.email == user.email).values(cn=f'sec{user.id}')
        await self.result(statement)

    async def update_user_created(self, user: UserId, created: datetime):
        statement = update(Users).where(Users.email == user.email).values(created=created)
        await self.result(statement)

    async def delete_user(self, email: str):
        statement = delete(Users).where(Users.email == email)
        await self.result(statement)

    async def delete_lookingtobuy(self, email: str):
        statement = delete(BuyFormFilling).where(BuyFormFilling.email == email)
        await self.result(statement)


dbq = DbQuery()
