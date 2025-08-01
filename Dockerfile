FROM ubuntu:22.04 AS production

RUN apt-get update && apt-get install -y cron bash
RUN apt-get update && apt-get install -y dnsutils
RUN getent group www-data || groupadd -r www-data && \
    id -u www-data || useradd -r -g www-data -s /usr/sbin/nologin www-data
WORKDIR /whoer
COPY config.py config.py
COPY cert_gen cert_gen/
COPY crontabs crontabs/
COPY libs libs/
COPY langs langs/
COPY dbm dbm/
COPY grpc_lib grpc_lib/
WORKDIR /whoer/crontabs
RUN touch /var/log/cron.log && chmod 0666 /var/log/cron.log
RUN mkdir -p /var/run && chown www-data:www-data /var/run
RUN touch /var/log/cron.log && chown www-data:www-data /var/log/cron.log
COPY crontabs/crontab /etc/cron.d/appcron
RUN chmod 0644 /etc/cron.d/appcron

# RUN apt-get update -y && apt-get install cron -y
RUN apt-get update && apt-get install -y python3-pip
RUN pip3 install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["cron", "-f"]