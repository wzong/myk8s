#!/bin/bash

function check_arg() {
  if [[ -z $3 ]]; then
    echo "Required argument not provided: $1"
    exit 1
  else
    echo "$2: $3"
  fi  
}

check_arg "EMAIL" "SSL Email" $1
check_arg "DOMAIN" "SSL Domain" $2
check_arg "INGRESS" "INGRESS Address" $3

email=$1
domain=$2
ingress=$3

# Remove all docker containers
docker rm -fv  $(docker ps -a -q)
# Remove all docker volumes
docker volume rm -f $(docker volume ls)
# Remove all cluster data
rm -rf /run/secrets/kubernetes.io
rm -rf /var/lib/etcd
rm -rf /var/lib/kubelet
rm -rf /var/lib/rancher
rm -rf /etc/kubernetes
rm -rf /opt/rke

# Rancher server
docker run -d --restart=unless-stopped \
 --name=rancher-server \
 -v /var/myk8s/rancher:/var/lib/rancher \
 -v /etc/letsencrypt/live/$domain/chain.pem:/etc/rancher/ssl/cacerts.pem \
 -v /etc/letsencrypt/live/$domain/cert.pem:/etc/rancher/ssl/cert.pem \
 -v /etc/letsencrypt/live/$domain/privkey.pem:/etc/rancher/ssl/key.pem \
 rancher/rancher

# HTTPS gateway
docker run --restart=always \
  -p 80:80 -p 443:443 \
  -v /etc/letsencrypt:/etc/letsencrypt \
  --link rancher-server:rancher-server \
  --name rancher-ssl \
  -d -e EMAIL=$email -e DOMAIN=$domain \
  -e INGRESS_HTTP=http://$ingress:30001 -e INGRESS_HTTPS=https://$ingress:30002 \
  wzong/myk8s-https

