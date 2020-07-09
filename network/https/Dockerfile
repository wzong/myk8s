FROM nginx

RUN apt-get update
RUN apt-get install -y bc cron certbot
RUN rm -rf /var/lib/apt/lists/*

RUN mkdir -p /usr/src
WORKDIR /usr/src
COPY . /usr/src

RUN echo "0 12,6 * * * /usr/src/renew.sh" | tee -a /var/spool/cron/root \
    && chmod +x /usr/src/renew.sh \
    && chmod +x /usr/src/start.sh

RUN /etc/init.d/cron start \
    && update-rc.d cron defaults

CMD ["/bin/sh", "-c", "./start.sh"]

