#!/bin/bash
. crons/env.sh
/usr/bin/python3 scripts/vpn_get_online_users_and_bw.py >> /var/log/cron.log 2>&1