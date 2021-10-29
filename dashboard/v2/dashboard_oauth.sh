#!/bin/sh

export OAUTH2_PROXY_COOKIE_SECRET="$(python -c 'import os,base64; print(base64.b64encode(os.urandom(16)).decode("ascii"))')"

echo "
injectRequestHeaders:
- name: Authorization
  values:
  - value \"Bearer $DASHBOARD_SA_TOKEN\"
" > /bin/alpha_config.txt

/bin/oauth2-proxy --alpha-config=/bin/alpha_config.txt $@