import unittest


from cluster.base import base
from cluster.ip import ip
from cluster.loadbalancer import loadbalancer
from cluster.protos import ip_pb2


_TEST_NGINX_SETUP = '''# TCP LoadBalancer
sudo echo 'stream {
  upstream port_16443 {
    server 10.2.0.2:6443;
    server 10.2.8.2:6443;
    server 10.2.16.2:6443;
  }
  server {
    listen 16443;
    proxy_pass port_16443;
  }
}' > /etc/nginx/nginx.conf'''

class LoadBalancerTest(unittest.TestCase):

  def setUp(self):
    self.cluster_subnet = ip.ClusterSubnet('mv', ip_pb2.Subnet(address='10.2.0.0', netmask=16))

  def test_GetNginxSetup(self):
    kube_control_planes = [base.NodeId('mvaa01'), base.NodeId('mvba01'), base.NodeId('mvca01')]
    lb = loadbalancer.LoadBalancer(self.cluster_subnet, kube_control_planes)
    self.assertEqual(lb.GetNginxSetup(), _TEST_NGINX_SETUP)


if __name__ == "__main__":
    unittest.main()
