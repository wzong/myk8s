#!/bin/bash

set -e

if [ ! -d /etc/letsencrypt/live/$DOMAIN ]; then
  certbot certonly --noninteractive --agree-tos --email $EMAIL --standalone -d *.$DOMAIN -d $DOMAIN
fi

function check_arg() {
  if [[ -z $3 ]]; then
    echo "Required argument not provided: $1"
    exit 1
  else
    echo "$2: $3"
  fi
}
check_arg "EMAIL" "SSL Email" $EMAIL
check_arg "DOMAIN" "SSL Domain" $DOMAIN
check_arg "BACKEND_HTTP" "Backend http" $BACKEND_HTTP
check_arg "BACKEND_HTTPS" "Backend https" $BACKEND_HTTPS

sed "s,<DOMAIN>,$DOMAIN,g" ./nginx.conf \
| sed "s,<BACKEND_HTTPS>,$BACKEND_HTTPS,g" \
| sed "s,<BACKEND_HTTP>,$BACKEND_HTTP,g" > /etc/nginx/nginx.conf

nginx -g "daemon off; error_log /dev/stderr notice;"
