domain=$1
echo "Ingress host: $domain"

SCRIPT_DIR=$(dirname "$0")
sed "s/<DOMAIN>/$domain/" $SCRIPT_DIR/deploy.yaml > /tmp/kubernetes_dashboard.yaml
kubectl apply -f /tmp/kubernetes_dashboard.yaml

