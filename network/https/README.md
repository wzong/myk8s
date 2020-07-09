# HTTPS for Ingress and Rancher servers

## Overview

The cluster could have multiple public-facing HTTP servers which need
HTTPS protections:

* Rancher: If using Rancher to manage the k8s, Rancher server must be up and
  accessible with SSL certificate from Certificate Authority, even before the
  k8s cluster is created.
* Ingress: If using ingress, after the k8s cluster is created, the
  [Ingress](../ingress/README.md) can be deployed to the cluster. The Ingress
  can allow services to be accessed by their hostnames (subdomains) instead 
  of port number.

The solution was based on [rancher-ssl](https://github.com/dewe/rancher-ssl)
project, which is a docker image with the following:

* Nginx server listenining on 80 and 443 ports to serve HTTP/HTTPS traffic,
  which forwards the traffic to Rancher/Ingress based on hostnames.
* Crontab that keeps refreshing the SSL certificate with the 
  [letsencrypt](https://letsencrypt.org/)

## Nginx config

The Nginx server has the following config:

* Wildcard SSL for `*.<DOMAIN>` from Certificate Authority 
* Redirect `rancher.<DOMAIN>` to the Rancher server with SSL redirect.
* Redirect `*.<DOMAIN>` to the Ingress server; it passes through http, and
  re-encrypts https.

## SSL certificate

The letsencrypt wildcard SSL cannot be obtained automatedly with
`--noninteractive`. See [link](https://developerinsider.co/how-to-create-and-auto-renew-lets-encrypt-wildcard-certificate/)
for the manual instructions.

This docker image expects certificate to be saved under
`/etc/letsencrypt/live/<DOMAIN>/` on the machine.

This docker image supports auto-renew the SSL certificates with certbot
crontab.

## Usage

Execute the following command to start HTTP/HTTPS proxy:

```shell
# @params $your_email The contact email to renew SSL
# @params $your_domain The SSL domain, e.g. example.com will use letsencrypt
#   SSL under /etc/letsencrypt/live/example.com/ and pass through
#   "*.example.com" to the backend
# @params $backend_http The backend endpoints to pass through HTTP traffic,
#   in form of "http://192.168.1.10:8080"; Please do not use "localhost"
#   because that will be routed to the docker container itself instead of the
#   local machine.
# @params $backend_https The backend endpoints to pass through HTTPS traffic,
#   simular with $backend_http
docker run --restart=always \
  -p 80:80 -p 443:443 \
  -v /etc/letsencrypt:/etc/letsencrypt \
  -d -e EMAIL=$your_email \
   -e DOMAIN=$your_domain \
  -e BACKEND_HTTP=$backend_http \
  -e BACKEND_HTTPS=$backend_https \
  wzong/myk8s-https
```

The Ingress can be accessed with `*.$your_domain`.


If using with the Rancher, add the following flag, and I need to start this
HTTPS proxy before opening the Rancher web UI:

```shell
  --link <rancher container name>:rancher-server \
```

The Rancher server can be accessed by `rancher.$your_domain`.
