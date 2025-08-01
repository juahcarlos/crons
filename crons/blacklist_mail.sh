#!/bin/bash

set -e

# Load env vars for Pydantic
# export $(grep -v '^#' /whoer/crontabs/env.vars | xargs)

# Set correct environment variables
export PYTHONPATH=/whoer:/whoer/crontabs
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# Optional: Log current time and environment for debugging
echo "[cron.sh] $(date): Starting cron job"

# Optional DNS test to confirm name resolution works
echo "[cron.sh] DNS test:" >> /var/log/cron.log
dig google.com @8.8.8.8 >> /var/log/cron.log 2>&1

# Run your Python script
echo "[cron.sh] Running vpn_load_blacklisted_email_list.py:" >> /var/log/cron.log
cd /whoer/crontabs
/usr/bin/python3 scripts/vpn_load_blacklisted_email_list.py misc/burning-emails.txt >> /var/log/cron.log 2>&1