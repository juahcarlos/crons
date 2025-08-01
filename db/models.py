from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    Index,
    Integer,
    String,
    Text,
    TIMESTAMP,
    VARCHAR,
)
from sqlalchemy.types import DECIMAL
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ServersConfig(Base):
    __tablename__ = "servers_config"

    id = Column(BigInteger, primary_key=True)
    server = Column(String(64), default="", nullable=False)
    enabled = Column(Boolean, default=False, nullable=False)
    hidden = Column(Boolean, default=False, nullable=False)
    auto_visibility = Column(Boolean, default=False, nullable=False)
    iso = Column(VARCHAR(2), default='-', nullable=True)
    country = Column(VARCHAR(50), default="", nullable=True)
    city = Column(VARCHAR(50), default="", nullable=True)
    ip = Column(VARCHAR(15), default="", nullable=True)
    remote_ips = Column(Text, default="", nullable=True)
    trial = Column(Boolean, default=False, nullable=True)
    openvpn = Column(Boolean, default=False, nullable=True)
    ikev2 = Column(Boolean, default=False, nullable=True)
    proxy = Column(Boolean, default=False, nullable=True)
    l2tp = Column(Boolean, default=False, nullable=True)
    l2tp_raw = Column(Boolean, default=False, nullable=True)
    l2tp_ipsec = Column(Boolean, default=False, nullable=True)
    sstp = Column(Boolean, default=False, nullable=True)
    softether = Column(Boolean, default=False, nullable=True)

    __table_args__ = (Index('server', "server", unique=True),)


class ServersConfigDev(Base):
    __tablename__ = "servers_config_dev"

    id = Column(BigInteger, primary_key=True)
    server = Column(String(64), default="", nullable=False)
    enabled = Column(Boolean, default=False, nullable=False)
    hidden = Column(Boolean, default=False, nullable=False)
    auto_visibility = Column(Boolean, default=False, nullable=False)
    iso = Column(VARCHAR(2), default='-', nullable=True)
    country = Column(VARCHAR(50), default="", nullable=True)
    city = Column(VARCHAR(50), default="", nullable=True)
    ip = Column(VARCHAR(15), default="", nullable=True)
    remote_ips = Column(Text, default="", nullable=True)
    trial = Column(Boolean, default=False, nullable=True)
    openvpn = Column(Boolean, default=False, nullable=True)
    ikev2 = Column(Boolean, default=False, nullable=True)
    proxy = Column(Boolean, default=False, nullable=True)
    l2tp = Column(Boolean, default=False, nullable=True)
    l2tp_raw = Column(Boolean, default=False, nullable=True)
    l2tp_ipsec = Column(Boolean, default=False, nullable=True)
    sstp = Column(Boolean, default=False, nullable=True)
    softether = Column(Boolean, default=False, nullable=True)

    __table_args__ = (Index('server', "server", unique=True),)


class Users(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    email = Column(VARCHAR(150), default="", nullable=False)
    created = Column(TIMESTAMP, default=datetime.now(), nullable=False)
    cn = Column(String(100), default=None, nullable=True)
    trial = Column(Boolean, default=False, nullable=True)
    version_page = Column(Integer, default=0, nullable=True)
    code = Column(String(250), default=None, nullable=True)
    coupon = Column(String(250), default=None, nullable=True)
    expires = Column(Integer, default=None, nullable=True)
    plan = Column(Integer, default=None, nullable=True)
    country_iso = Column(String(2), default="-", nullable=True)
    password = Column(String(100), default="", nullable=True)
    reg_source = Column(String(100), default="web", nullable=True)
    dubious = Column(Boolean, default=False, nullable=False)
    subscribed = Column(Boolean, default=False, nullable=False)
    lang = Column(String(2), default="en", nullable=False)
    partner_id = Column(BigInteger, default=None, nullable=True)
    note = Column(Text, default=None, nullable=True)

    __table_args__ = (
        Index('id', "id", unique=True),
        Index('users_code_expires', "code", "expires"),
        Index('users_trial', "trial"),
        Index('users_dubious', "dubious"),
        Index('users_expires', "expires", mysql_using='BTREE'),
        Index('users_created', "created"),
        Index('users_dubious', "dubious"),
        Index('trial_expires', "trial", "expires"),
    )


class VpnServersStat(Base):
    __tablename__ = "vpn_servers_stat"

    id = Column(BigInteger, primary_key=True)
    server = Column(String(64))
    created = Column(DateTime)
    online_vpn = Column(Integer)
    online_proxy = Column(Integer)
    traf_today = Column(Integer)
    traf_yesterday = Column(Integer)
    traf_month = Column(Integer)
    bandwidth_today = Column(VARCHAR(64))
    bandwidth_yesterday = Column(VARCHAR(64))
    bandwidth_month = Column(VARCHAR(64))
    online_l2tp = Column(Integer)
    online_sstp = Column(Integer)
    online_softether_native = Column(Integer)
    wman_version = Column(String(64))


class BuyFormFilling(Base):
    __tablename__ = "buy_form_filling"

    id = Column(BigInteger, primary_key=True)
    created = Column(TIMESTAMP, default=datetime.now(), nullable=False)
    email = Column(VARCHAR(150), default="", nullable=False)
    lang = Column(String(2), default="en", nullable=False)

    __table_args__ = (
        Index('id', "id", unique=True),
        Index('created', "created"),
        Index('email', "email"),
    )


class Transactions(Base):
    __tablename__ = "transactions"

    id = Column(BigInteger, primary_key=True)
    system = Column(String(100), default=None, nullable=True)
    data = Column(Text)
    days = Column(Integer)
    amount = Column(DECIMAL(10, 2))
    email = Column(VARCHAR(250), default="", nullable=True)
    expires = Column(TIMESTAMP, default=datetime.now(), nullable=False)
    created = Column(TIMESTAMP, default=datetime.now(), nullable=False)
    trial = Column(Boolean, default=True, nullable=False)
    coupon = Column(String(250), default=None, nullable=True)
    version_page = Column(Integer)
    country_iso = Column(String(2), default="-", nullable=True)
    complete = Column(Boolean, default=False, nullable=True)
    partner_amount = Column(DECIMAL(10, 2))
    partner_id = Column(BigInteger, default=0, nullable=True)
    partner_referrer_id = Column(BigInteger, default=0, nullable=False)
    pushed_by = Column(String(250), default=None, nullable=True)
    remote_amount = Column(DECIMAL(10, 2))
    check_order_id = Column(BigInteger, default=0, nullable=False)
    pay_time = Column(Integer)
    remote_status = Column(VARCHAR(255), default=None, nullable=True)
    credited = Column(String(255), default=None, nullable=True)
    json_custom_fields = Column(String(8000))
    remote_invoice_id = Column(String(8000))
    refund = Column(DECIMAL(10, 2), default=0, nullable=False)

    __table_args__ = (
        Index('transactions_email', "email"),
        Index('transactions_email_complete', "email", "complete"),
        Index('transactions_trial', "trial"),
        Index('transactions_created', "created"),
        Index('transactions_expires', "expires"),
        Index('transactions_partner_id', "partner_id"),
        Index('transactions_coupon', "coupon", "created"),
        Index('transactions_complete_created', "complete", "created"),
    )


class StatChurnRate(Base):
    __tablename__ = "stat_churn_rate"

    id = Column(BigInteger, primary_key=True)
    year = Column(BigInteger, nullable=False)
    month = Column(BigInteger, default=None, nullable=True)
    users_in_end_of_prev_period = Column(BigInteger, nullable=False, default=0)
    new_users_in_curr_period = Column(BigInteger, nullable=False, default=0)
    users_in_end_of_curr_period = Column(BigInteger, nullable=False, default=0)
    churn_rate = Column(DECIMAL(10, 2), nullable=False, default=0)

    __table_args__ = (
        Index('id', "id", unique=True),
        Index('stat_churn_rate_uniq', "year", "month", unique=True),
    )


class StatMetrics(Base):
    __tablename__ = "stat_metrics"

    id = Column(BigInteger, primary_key=True)
    alias = Column(VARCHAR(250), default="", nullable=True)
    name = Column(VARCHAR(250), default="", nullable=True)

    __table_args__ = (
        Index('id', "id", unique=True),
        Index('alias', "alias", unique=True),
    )


class Stat(Base):
    __tablename__ = "stat"

    id = Column(BigInteger, primary_key=True)
    metric_id = Column(BigInteger, default=None, nullable=True)
    date = Column(Date, default=datetime.now, nullable=True)
    value = Column(BigInteger, default=None, nullable=True)
    ext = Column(Text)

    __table_args__ = (
        Index('id', "id", unique=True),
        Index('metric_id', "metric_id", unique=True),
    )
