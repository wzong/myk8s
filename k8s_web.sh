#!/bin/bash
# https://kubernetes.io/docs/tasks/access-application-cluster/web-ui-dashboard/

kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.0.0-beta4/aio/deploy/recommended.yaml
server=$(kubectl config view -o jsonpath='{.clusters[0].cluster.server}')
echo ""
echo "Web UI:"
echo "  $server/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/"
echo ""
echo "Token:"
echo "  $(kubectl config view -o jsonpath='{.users[0].user.token}')"