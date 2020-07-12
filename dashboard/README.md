# Kubernetes Dashboard

Prerequisite:
* [HTTPS Proxy](/network/https/README.md)
* [Ingress](/network/ingress/README.md)

First create the deployment and services:

```shell
kubectl apply -f https://github.com/kubernetes/dashboard/raw/v2.0.3/aio/deploy/recommended.yaml
```

Second create an Ingress rule so that the dashboard can be accessed publicly
without `kubectl proxy`:

```shell
bash deploy.sh <DASHBOARD_SUB_DOMAIN>
```

