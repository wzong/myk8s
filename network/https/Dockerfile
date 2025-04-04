FROM nginx

# Install cron, python3
RUN apt-get update
RUN apt-get install -y cron python3-pip python3-venv
RUN rm -rf /var/lib/apt/lists/*

# Install certbot and cloudflare plugins in venv
RUN python3 -m venv /opt/certbot/
RUN /opt/certbot/bin/pip install --upgrade pip
RUN /opt/certbot/bin/pip install certbot certbot-dns-cloudflare

# Copy source files
RUN mkdir -p /usr/src
WORKDIR /usr/src
COPY . /usr/src

# Make the scripts executable
RUN chmod +x /usr/src/renew.sh && chmod +x /usr/src/start.sh

# Set up crontab to run renew.sh every Sunday at 12pm
RUN echo "0 12 * * 0 /usr/src/renew.sh" | crontab -
RUN /etc/init.d/cron start && update-rc.d cron defaults

# Initialize certificate and start nginx reverse proxy server
CMD ["/bin/sh", "-c", "./start.sh"]

