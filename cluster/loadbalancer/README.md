# TCP Load Balancer

The following requires TCP load balancer:

<table>
  <tr>
    <th>Usage</th>
    <th>Backends</th>
    <th>Port</th>
    <th>Backend Port</th>
    <th>Doc</th>
  </tr>
  <tr>
    <td>Create HA Kubernetes cluster</td>
    <td>All healthy control plane nodes</td>
    <td>16443</td>
    <td>6443</td>
    <td>
      <a href="https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/high-availability/">link</a>
    </td>
  </tr>
  <tr>
    <td>Ingress HTTP/HTTPS</td>
    <td>Nodes where the Nginx Ingress Pods runs</td>
    <td>80/443</td>
    <td>30080/30443</td>
    <td></td>
  </tr>
</table>
