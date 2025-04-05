#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source ${SCRIPT_DIR}/common.sh

# Print certbot plugins
/opt/certbot/bin/certbot plugins

# Renew cert and reload nginx
/opt/certbot/bin/certbot renew "$@"
nginx -s reload
