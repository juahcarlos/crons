#!/bin/bash

. crons/env.sh
/usr/bin/python3 scripts/vpn_send_payment_reminder.py >> /var/log/cron.log 2>&1