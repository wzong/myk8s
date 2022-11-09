kubectl apply -f test_k8s_storage.yaml
export INGRESS_HOST=storage.$1 && \
export OAUTH2_HOST=login.$1 && \
export BACKEND_SERVICE_NAME=storage-service && \
export BACKEND_SERVICE_NAMESPACE=default && \
cat ../auth/ingress_http.template.yaml | \
envsubst '${OAUTH2_HOST} ${INGRESS_HOST} ${BACKEND_SERVICE_NAME} ${BACKEND_SERVICE_NAMESPACE}' | \
kubectl apply -f -