#!/bin/bash

. crons/env.sh
/usr/bin/python3 scripts/lookingtobuy.py >> /var/log/cron.log 2>&1