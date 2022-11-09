export OAUTH2_HOST=dashboard.$1 &&
export BACKEND_SERVICE_NAME=kubenetes-dashboard && \
export BACKEND_SERVICE_NAMESPACE=kubernetes-dashboard && \
cat ../../auth/ingress_app.template.yaml | envsubst | kubectl apply -f -