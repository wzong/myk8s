docker rm -fv  $(docker ps -a -q) 
docker volume rm -f $(docker volume ls)
rm -rf /run/secrets/kubernetes.io
rm -rf /var/lib/etcd
rm -rf /var/lib/kubelet
rm -rf /var/lib/rancher
rm -rf /etc/kubernetes
rm -rf /opt/rke
docker run -d --restart=unless-stopped \
 -p 8080:80 -p 443:443 \
 -v /var/tinymakecloud/rancher:/var/lib/rancher \
 -v /var/tinymakecloud/certs/cacert.pem:/etc/rancher/ssl/cacerts.pem \
 -v /var/tinymakecloud/certs/certificate.pem:/etc/rancher/ssl/cert.pem \
 -v /var/tinymakecloud/certs/private.pem:/etc/rancher/ssl/key.pem \
 rancher/rancher
