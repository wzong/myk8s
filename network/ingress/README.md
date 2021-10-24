# Ingress for k8s services

## Overview

The goal is to allow k8s services to be exposed to the public network.
K8s provided the following ways:

* `NodePort`: Each service must reserve a static port on the node machine,
  so that it can be reached via port number with (any of) the node IP.
  Therefore, I need to remember IP+Port for each service. Also, for
  self-hosted cluster behind NAT, I need to set up port forwarding for each
  service.
* `LoadBalancer`: one L4 load balancer needs to be brought up for each
  service, which is very difficult to achieve with self-hosted cluster.
  Also, each LB requires an IP address, each of which would requires port
  forwarding if behind NAT.
* `Ingress`: a NodePort service that routes traffic to other `ClusterIP`
  services based on the hostname and/or path; This is very desirable for
  my self-hosted k8s cluster since I can only set up port forwarding once
  and it works for all services.

## Nginx-Ingress

For Ingress, I'm using the bare-metal solution from
[nginx-ingress](https://kubernetes.github.io/ingress-nginx/)

The standard deployment does not work out-of-box, so minor changes are made:

* Use fixed `nodePort` (30001 & 30002) for http/https, otherwise k8s will
  auto-assign a port, which makes it more difficult for me to set up port
  forwarding (sometimes I destroy the re-create the cluster to test features.
  so I want the ports to be static to avoid reconfiguring port forwarding).

## SSL certificate

The default self-signed certificate is used, because I want to use a separate
[HTTPS proxy server](../https/README.md) to pass through and re-encrypt the
traffic to the Ingress. The benefits are:

* I can configure custom routing rules which are not managed by Ingress.
* It's easier and more flexible to auto-renew the CA-signed certificate (e.g.
  use crontab in the proxy docker image vs hack the nginx deployment)

## Usage

After k8s cluster is ready, simply execute:

```
kubectl apply -f https://raw.githubusercontent.com/wzong/myk8s/master/network/ingress/ingress.yaml
```

## SSL pass through

For this version of nginx-ingress controller, the following annotations
are needed if the service is already an HTTPS service:

```yaml
apiVersion: networking.k8s.io/v1beta1
kind: Ingress
metadata:
  ......
  annotations:
    # use the shared ingress-nginx
    kubernetes.io/ingress.class: "nginx"
    nginx.ingress.kubernetes.io/ssl-passthrough: "true"
    nginx.ingress.kubernetes.io/backend-protocol: "HTTPS"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  rules:
  - host: <SUB_DOMAIN>
    http:
      paths:
      - path: /
        backend:
          serviceName: my-https-service 
          servicePort: 443
```
