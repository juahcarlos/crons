from datetime import date, datetime, timedelta

from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class User(BaseModel):
    email: EmailStr = Field(default=None)
    created: Optional[datetime | str] = datetime.now()
    cn: Optional[str] = ""
    trial: Optional[bool | int | None] = 0
    version_page: Optional[int] = 2
    code: Optional[str] = ""
    coupon: Optional[str] = ""
    expires: Optional[int | str | None] = int((datetime.now() + timedelta(days=30)).strftime("%s"))
    plan: Optional[int | None]
    country_iso: Optional[str] = ""
    password: Optional[str] = ""
    reg_source: Optional[str] = ""
    dubious: Optional[bool | int] = 0
    subscribed: Optional[bool | int] = 0
    lang: Optional[str] = ""
    partner_id: Optional[int | None] = 0
    note: Optional[str] = ""


class UserId(User):
    id: int


class UserReminder(UserId):
    unsubscribe_token: Optional[str] = ""


class UserDateCount(BaseModel):
    date: datetime
    value: int


class RemoteIp(BaseModel):
    ip: str


class ServerManage(BaseModel):
    url: str
    key: str


class ServerDb(BaseModel):
    id: Optional[int] = None
    server: Optional[int | str] = ""
    enabled: Optional[int | bool] = True
    hidden: Optional[int | bool] = False
    auto_visibility: Optional[int | bool] = True
    iso: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    ip: Optional[str] = None
    remote_ips: Optional[str] = ""
    trial: Optional[int | bool] = False
    openvpn: Optional[int | bool] = False
    ikev2: Optional[int | bool] = False
    proxy: Optional[int | bool] = False
    l2tp: Optional[int | bool] = False
    l2tp_raw: Optional[int | bool] = False
    l2tp_ipsec: Optional[int | bool] = False
    sstp: Optional[int | bool] = False
    softether: Optional[int | bool] = False


class Server(BaseModel):
    name: str
    manage: ServerManage
    iso: str
    country: str
    city: str
    ip: str
    remote_ips: List[RemoteIp]
    hostname: str
    trial: int
    openvpn: int
    ikev2: int
    proxy: int


class Servers(BaseModel):
    servers_conf: List[Server]


class ServerSrv(BaseModel):
    server: str


class TransCountryMailCount(BaseModel):
    country: str
    cvalue: int


class TransDateCount(BaseModel):
    date: date
    count: int


class TransDateDaysCount(BaseModel):
    date: date
    days: int
    count: int


class TransDatePlanCount(BaseModel):
    date: date
    plan: int | str
    count: int


class UsersDateCount(BaseModel):
    date: date
    cvalue: int


class VpnStat(BaseModel):
    server: str
    # created: str
    online_vpn: int = 0
    online_proxy: int = 0
    traf_today: int = 0
    traf_yesterday: int = 0
    traf_month: int = 0
    bandwidth_today: str
    bandwidth_yesterday: str
    bandwidth_month: str
    wman_version: str


class BuyFormFill(BaseModel):
    address: Optional[str | None] = None
    lang: str = "en"
    users_id: int


class MailData(BaseModel):
    email: str
    from_email: str
    subject: str
    body: str


class Coupons(BaseModel):
    coupon: str
    percent: int
    created: Optional[datetime | None] = None
    expiration: datetime
    plans: Optional[str | None] = None


class ReminderArgs(BaseModel):
    try_one_email: Optional[str | None] = None
    no_unsubscribe: Optional[bool] = None


class CustomerPromo(BaseModel):
    address: str
    lang: str


class TransCount(BaseModel):
    count: int


class TransPaymentAmount(BaseModel):
    date: date
    system: str
    sum: float | int


class ChurnRate(BaseModel):
    year: Optional[int | None] = None
    month: Optional[int | None] = None
    users_in_end_of_prev_period: int
    users_new_current_period: int
    users_in_end_of_current_period: int
    churn_rate: float


class ChurnRateId(BaseModel):
    id: int


class StatMetricsDB(BaseModel):
    id: int
    alias: str
    name: str


class StatDB(BaseModel):
    id: Optional[int] = None
    metric_id: Optional[int] = None
    date: Optional[date] = None
    value: Optional[int] = None
    ext: Optional[str] = None

    @field_validator("date", mode="plain")
    @classmethod
    def parse_date(cls, v):
        if isinstance(v, str):
            return datetime.strptime(v, "%Y-%m-%d").date()
        return v


class PlanCount(BaseModel):
    plan: int | str
    count: int
