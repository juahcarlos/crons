#!/bin/bash
. crons/env.sh
/usr/bin/python3 scripts/sync_softether_users.py >> /var/log/cron.log 2>&1