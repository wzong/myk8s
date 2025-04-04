#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source ${SCRIPT_DIR}/common.sh

# Required arguments
check_arg "EMAIL" "SSL Email" $EMAIL
check_arg "DOMAIN" "SSL Domain" $DOMAIN

# Print certbot plugins
/opt/certbot/bin/certbot plugins

# Initialize wildcard certificate if not exist
if [ ! -d /etc/letsencrypt/live/$DOMAIN ]; then
  /opt/certbot/bin/certbot certonly \
    --agree-tos \
    --authenticator dns-cloudflare \
    --dns-cloudflare-credentials /etc/letsencrypt/cloudflare.ini \
    --dns-cloudflare-propagation-seconds 90 \
    --keep-until-expiring --non-interactive --expand \
    -d "$DOMAIN" \
    -d "*.$DOMAIN"
fi
