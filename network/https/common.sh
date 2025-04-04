# Verify required env vars are provided
function check_arg() {
  if [[ -z $3 ]]; then
    echo "Required argument not provided: $1"
    exit 1
  else
    echo "$2: $3"
  fi
}

# Verify cloudflare credential is provided
if [ ! -f /etc/letsencrypt/cloudflare.ini ]; then
  echo "File /etc/letsencrypt/cloudflare.ini does not exist"
  exit 1
fi
