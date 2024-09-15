from cluster.base import base
from cluster.ip import ip

PORT_KUBE_CONTROL_PLANE = 6443
PORT_KUBE_CONTROL_PLANE_LB = 16443

class LoadBalancer(object):

  def __init__(
    self,
    cluster_subnet: ip.ClusterSubnet,
    kube_control_planes: list[base.NodeId]):
    self.cluster_subnet = cluster_subnet
    self.kube_control_planes = kube_control_planes

  def GetNginxConfig(self):
    result = ['stream {']
    if self.kube_control_planes:
      result.append('  upstream port_%d {' % PORT_KUBE_CONTROL_PLANE_LB)
      for node_id in self.kube_control_planes:
        node_ip = self.cluster_subnet.GetNodeIp(node_id)
        result.append('    server %s:%d;' % (node_ip, PORT_KUBE_CONTROL_PLANE))
      result.append('  }')

    if self.kube_control_planes:
      result.extend([
        '  server {',
        '    listen %d;' % PORT_KUBE_CONTROL_PLANE_LB,
        '    proxy_pass port_%d;' % PORT_KUBE_CONTROL_PLANE_LB,
        '  }',
      ])
    result.append('}')
    return '\n'.join(result)

  def GetNginxSetup(self):
    return '# TCP LoadBalancer\nsudo echo \'' + self.GetNginxConfig() + '\' > /etc/nginx/nginx.conf'
