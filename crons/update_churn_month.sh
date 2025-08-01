#!/bin/bash

. crons/env.sh
/usr/bin/python3 scripts/update_active_users_churn_rate.py --month --pid=update-active-users-churn-rate-month.pid>> /var/log/cron.log 2>&1