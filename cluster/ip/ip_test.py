import json
import unittest

from google.protobuf import text_format
from cluster.base import base
from cluster.ip import ip
from cluster.protos import base_pb2
from cluster.protos import ip_pb2


_TEST_CLUSTER_SUBNET = '''
address: "10.2.0.0"
netmask: 16
children {
  address: "10.2.0.0"
  netmask: 26
  gateways {
    to: '0.0.0.0/0'
    via: '10.2.0.1'
  }
}
children {
  address: "10.2.2.0"
  netmask: 24
}
gateways {
  to: '0.0.0.0/0'
  via: '10.2.3.1'
}
'''

_TEST_NETPLAN = '''# Netplan eth0
network:
  ethernets:
    eth0:
      addresses: 10.2.0.2/26
      dhcp4: false
      nameservers:
        addresses:
        - 8.8.8.8
        - 1.1.1.1
      routes:
      - to: 0.0.0.0/0
        via: 10.2.0.1
  version: 2
'''


class IpTest(unittest.TestCase):

  def setUp(self):
    self.subnet = text_format.Parse(_TEST_CLUSTER_SUBNET, ip_pb2.Subnet())
    self.cluster = ip.ClusterSubnet('mv', self.subnet)

  def test_Subnet(self):
    subnet = self.cluster.subnet
    self.assertEqual(subnet.address, '10.2.0.0')
    self.assertEqual(subnet.netmask, 16)
    self.assertEqual(subnet.broadcast, '10.2.255.255')

  def test_InvalidClusterId(self):
    with self.assertRaises(ValueError) as e:
      self.cluster = ip.ClusterSubnet('invalid', self.subnet)
    self.assertIn('Invalid ClusterSubnet.cluster_id', str(e.exception))

  def test_InvalidAddress(self):
    self.subnet.address = '10.2.1.0'
    with self.assertRaises(ValueError) as e:
      self.cluster = ip.ClusterSubnet('mv', self.subnet)
    self.assertIn('Invalid Subnet.address: network address must be 0th', str(e.exception))

  def test_InvalidChildAddress(self):
    self.subnet.children.append(ip_pb2.Subnet(address = '10.3.1.0', netmask = 24))
    with self.assertRaises(ValueError) as e:
      self.cluster = ip.ClusterSubnet('mv', self.subnet)
    self.assertIn('Invalid Subnet.address: not a child subnet', str(e.exception))

  def test_GetNodeAddress(self):
    # Child subnet 10.2.0.0/26
    self.assertEqual(self.cluster.GetNodeAddress(base.NodeId('mvaa00')), '10.2.0.1/26')
    self.assertEqual(self.cluster.GetNodeAddress(base.NodeId('mvaa61')), '10.2.0.62/26')

    # Cluster 10.2.0.0/16
    self.assertEqual(self.cluster.GetNodeAddress(base.NodeId('mvab00')), '10.2.0.65/16')
    self.assertEqual(self.cluster.GetNodeAddress(base.NodeId('mvab61')), '10.2.0.126/16')

    # Child subnet 10.2.2.0/24
    self.assertEqual(self.cluster.GetNodeAddress(base.NodeId('mvai00')), '10.2.2.1/24')
    self.assertEqual(self.cluster.GetNodeAddress(base.NodeId('mval61')), '10.2.2.254/24')

    # Cluster 10.2.0.0/16
    self.assertEqual(self.cluster.GetNodeAddress(base.NodeId('mvam00')), '10.2.3.1/16')
    self.assertEqual(self.cluster.GetNodeAddress(base.NodeId('mvba00')), '10.2.8.1/16')
    self.assertEqual(self.cluster.GetNodeAddress(base.NodeId('mvia00')), '10.2.64.1/16')
    self.assertEqual(self.cluster.GetNodeAddress(base.NodeId('mvzz61')), '10.2.206.126/16')

  def test_GetAllNodeIps_FitAllRacks(self):
    # Subnet size can fit all racks [aa - zz]
    node_ips = self.cluster.GetAllNodeIps()
    self.assertEqual(len(node_ips), 26 * 26 * 62)

    # Verifies no duplicate ip addresses are assigned to different nodes
    self.assertEqual(len(set([v for v in node_ips.values()])), len(node_ips))

  def test_GetAllNodeIps_FitOneRack(self):
    self.subnet.netmask = 26
    self.subnet.children.clear()
    self.cluster = ip.ClusterSubnet('mv', self.subnet)

    # Subnet size can only fit aa rack
    node_ips = self.cluster.GetAllNodeIps()
    self.assertEqual(len(node_ips), 62)

    # Verifies no duplicate ip addresses are assigned to different nodes
    self.assertEqual(len(set([v for v in node_ips.values()])), len(node_ips))

  def test_GetNodeNetplan(self):
    self.assertEqual(self.cluster.GetNodeNetplan(base.NodeId('mvaa01'), 'eth0'), _TEST_NETPLAN)


if __name__ == "__main__":
    unittest.main()
