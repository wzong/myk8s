#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source ${SCRIPT_DIR}/common.sh

# Required arguments
check_arg "DOMAIN" "SSL Domain" $DOMAIN
check_arg "BACKEND_HTTP" "Backend http" $INGRESS_IP

# Set up Nginx reverse proxy config
cat /usr/src/nginx.conf | \
  envsubst '${INGRESS_IP},${DOMAIN}' | \
  tee /etc/nginx/nginx.conf

# Start Nginx server
nginx -g "daemon off; error_log /dev/stderr notice;"
