# To rebuild:
# sudo docker build -f dashboard_oauth.Dockerfile -t wzong/kubernetes-dashboard-oauth-proxy .
# sudo docker push wzong/kubernetes-dashboard-oauth-proxy:latest
FROM bitnami/oauth2-proxy:latest

COPY ./dashboard_oauth.sh /bin/dashboard_oauth.sh
ENTRYPOINT ["/bin/dashboard_oauth.sh"]
