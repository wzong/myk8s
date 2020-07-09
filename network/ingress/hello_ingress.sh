domain=$1
echo "Ingress host: hello.$domain"

SCRIPT_DIR=$(dirname "$0")
sed "s/<DOMAIN>/$domain/" $SCRIPT_DIR/hello_ingress.yaml > /tmp/hello_ingress.yaml
kubectl apply -f /tmp/hello_ingress.yaml
