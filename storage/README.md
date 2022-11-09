# Persistent Storage

## Overview

K8S supports a wide range of
[persistent storage class](https://kubernetes.io/docs/concepts/storage/storage-classes/):
* Local: Using a local storage from a single specific Node is the easiest way. But in an
  HA k8s cluster, a Node can become unavailable.
* NFS: Many wireless routers and NAS (e.g. Synology NAS) can support NFS protocol and
  back-up-to-public-cloud features. They also proved to be more reliable than my aged
  computers for k8s nodes. Therefore, NFS should be a better choice for me in terms of
  availability and persistency.
* Glusterfs/Ceph/QuoByte: Open source or free distributed storage system that can be deployed
  on-premise. This should offer much better scalability and performance than the NFS approach.
  And some of them may be capable of backing up to cloud, or even directly use storage from
  popular cloud providers. However, they are much more complex to set up and maintain.
* Portworx/ScaleIO/StorageOS/vSphere: Cloud native storage provider that can be integrated
  with bare-metal k8s cluster. They should provide better persistency and availability than
  the self-hosted open-source storage system. They're also also maintenance free.
  However, up to 21H2, I found many of them still lack pricing details or documentations,
  and they often require a quote to get started.
* AWS/GCE/Azure/OpenStack: Up to 21H2, I found these persistent storage plugins
  does not seem to work on bare-metal k8s clusters (I could be wrong).
* configMap/emptyDir/hostPath: configMap is not a file system storage, and
  emptyDir/hostPath are not persistent enough since Pod can be rescheduled to a different
  Node. But emptyDir/hostPath should be good for ephemeral/temp storage.

Therefore, short-term wise, I decided to go with NFS (NAS + cloud backup) approach.

## Storage Provisioning

Since NFS storage supports `ReadWriteMany` mode, so that a single PersistentVolumnClaim (PVC)
can be mounted by multiple Pods at the same time as a global storage, and cross-pods sharing
is possible. Therefore, I end up statically provision a PVC for each of my NFS device.

See example at [nfs_example.yaml](./nfs_example.yaml) (In my case the NFS IP address is
`192.168.1.160` with `/var/nfs` as the path to use for k8s PV). To enable NFS on my cluster,
I also need to execute the following on each node

```shell
sudo apt-get install nfs-common -y
sudo service kubelet restart
```

To test that NFS is successfully mounted to multiple Pods, a `test_k8s_storage.yaml` deployment
is created to list files under the mounted directories.

```shell
kubectl apply -f test_k8s_storage.yaml
```

Optional: to configure an ingress endpoint behind oauth2-proxy:

```shell
bash test_k8s_storage.sh mysite.com
```
