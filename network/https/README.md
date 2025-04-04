# HTTPS for Ingress and Rancher servers

## Overview

The K8S [Ingress](/network/ingress/README.md) can route HTTP traffic for multiple virtual hosts.

To enable HTTPs for all of these virtual host, I use an Nginx server with
[Letsencrypt wildcard SSL certificate](https://letsencrypt.org/docs/faq/#does-let-s-encrypt-issue-wildcard-certificates)
as a [Reverse Proxy](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/) to route
"*.mysite.com" to the Ingress controller's static nodePort 30001/30002.

## SSL certificate

The letsencrypt wildcard SSL cannot be obtained automatedly with
`--noninteractive`. See [link](https://developerinsider.co/how-to-create-and-auto-renew-lets-encrypt-wildcard-certificate/)
for the manual instructions.

[This post](https://www.knyl.me/blog/set-up-wildcard-ssl-for-godaddy-domain-with-lets-encrypt) has
instruction of using certbot DNS plugins to auto create/renew wildcard certificates. It's done by
calling DNS provider's API to update TXT DNS records. To call the API, we need to get API key/token
from the provider to authenticate.

Unfortunately, Godaddy has shut down API access for accounts with less than 50 domains. I have to
transfer DNS nameserver to Cloudflare, which allows me to update DNS records via API.

## Docker Image

The Nginx Reverse Proxy + certbot scripts to create/renew wildcard certificates are composed
in a Docker image.

This docker image will save the certificates saved under
`/etc/letsencrypt/live/mysite.com/` on the machine.

This docker image will auto-renew the SSL certificates weekly with certbot crontab.

To rebuild:

```
sudo docker build -t wzong/myk8s-https .
sudo docker image push wzong/myk8s-https
```

## Usage

1. Get Cloudflare API
[credential](https://certbot-dns-cloudflare.readthedocs.io/en/stable/#credentials)
and save it to `/etc/letsencrypt/cloudflare.ini`

```shell
sudo mkdir -p /etc/letsencrypt/
echo "dns_cloudflare_api_token = $cloudflare_api_token" | sudo tee /etc/letsencrypt/cloudflare.ini
sudo chmod 400 /etc/letsencrypt/cloudflare.ini
```

1. Initialize SSL wildcard certificate with Letsencrypt:

```shell
sudo docker run -it --rm \
  -v /etc/letsencrypt:/etc/letsencrypt \
  -e EMAIL=admin@${your_domain} \
  -e DOMAIN=${your_domain} \
  wzong/myk8s-https bash /usr/src/init.sh
```

1. Start HTTP/HTTPS proxy:

```shell
sudo docker run -d --restart=always \
  -p 80:80 -p 443:443 \
  -v /etc/letsencrypt:/etc/letsencrypt \
  -e DOMAIN=${your_domain} \
  -e INGRESS_IP=${ingress_ip} \
  wzong/myk8s-https
```

The Ingress can be accessed with `*.$your_domain`.
