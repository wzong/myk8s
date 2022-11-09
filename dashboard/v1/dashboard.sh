kubectl apply -f dashboard.yaml
kubectl apply -f dashboard_admin.yaml
export INGRESS_HOST=dashboard.$1 && \
export OAUTH2_HOST=login.$1 && \
export BACKEND_SERVICE_NAME=kubernetes-dashboard && \
export BACKEND_SERVICE_NAMESPACE=kubernetes-dashboard && \
cat ../../auth/ingress_https.template.yaml | \
envsubst '${OAUTH2_HOST} ${INGRESS_HOST} ${BACKEND_SERVICE_NAME} ${BACKEND_SERVICE_NAMESPACE}' | \
kubectl apply -f -