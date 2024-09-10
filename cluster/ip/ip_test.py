import json
import unittest

from google.protobuf import text_format
from cluster.base import base
from cluster.base import base_pb2
from cluster.ip import ip
from cluster.ip import ip_pb2


_TEST_CLUSTER_SUBNET = '''
  cluster_id: "mv"
  subnet {
    address: "10.2.0.0"
    netmask: 16
    children {
      address: "10.2.0.0"
      netmask: 26
    }
    children {
      address: "10.2.2.0"
      netmask: 24
    }
  }
'''


class IpTest(unittest.TestCase):

  def setUp(self):
    self.config = text_format.Parse(_TEST_CLUSTER_SUBNET, ip_pb2.ClusterSubnet())
    self.cluster = ip.ClusterSubnet(self.config)

  def test_Subnet(self):
    subnet = self.cluster.subnet
    self.assertEqual(subnet.address, '10.2.0.0')
    self.assertEqual(subnet.netmask, 16)
    self.assertEqual(subnet.broadcast, '10.2.255.255')

  def test_InvalidClusterId(self):
    self.config.cluster_id = 'invalid'
    with self.assertRaises(ValueError) as e:
      self.cluster = ip.ClusterSubnet(self.config)
    self.assertIn('Invalid ClusterSubnet.cluster_id', str(e.exception))

  def test_InvalidAddress(self):
    self.config.subnet.address = '10.2.1.0'
    with self.assertRaises(ValueError) as e:
      self.cluster = ip.ClusterSubnet(self.config)
    self.assertIn('Invalid Subnet.address: network address must be 0th', str(e.exception))

  def test_InvalidChildAddress(self):
    self.config.subnet.children.append(ip_pb2.Subnet(address = '10.3.1.0', netmask = 24))
    with self.assertRaises(ValueError) as e:
      self.cluster = ip.ClusterSubnet(self.config)
    self.assertIn('Invalid Subnet.address: not a child subnet', str(e.exception))

  def test_GetNodeIp(self):
    # Child subnet 10.2.0.0/26
    self.assertEqual(self.cluster.GetNodeIp(base.NodeId('mvaa00')), '10.2.0.1/26')
    self.assertEqual(self.cluster.GetNodeIp(base.NodeId('mvaa61')), '10.2.0.62/26')

    # Cluster 10.2.0.0/16
    self.assertEqual(self.cluster.GetNodeIp(base.NodeId('mvab00')), '10.2.0.65/16')
    self.assertEqual(self.cluster.GetNodeIp(base.NodeId('mvab61')), '10.2.0.126/16')

    # Child subnet 10.2.2.0/24
    self.assertEqual(self.cluster.GetNodeIp(base.NodeId('mvai00')), '10.2.2.1/24')
    self.assertEqual(self.cluster.GetNodeIp(base.NodeId('mval61')), '10.2.2.254/24')

    # Cluster 10.2.0.0/16
    self.assertEqual(self.cluster.GetNodeIp(base.NodeId('mvam00')), '10.2.3.1/16')
    self.assertEqual(self.cluster.GetNodeIp(base.NodeId('mvba00')), '10.2.8.1/16')
    self.assertEqual(self.cluster.GetNodeIp(base.NodeId('mvia00')), '10.2.64.1/16')
    self.assertEqual(self.cluster.GetNodeIp(base.NodeId('mvzz61')), '10.2.206.126/16')

  def test_GetAllNodeIps_FitAllRacks(self):
    # Subnet size can fit all racks [aa - zz]
    node_ips = self.cluster.GetAllNodeIps()
    self.assertEqual(len(node_ips), 26 * 26 * 62)

    # Verifies no duplicate ip addresses are assigned to different nodes
    self.assertEqual(len(set([v for v in node_ips.values()])), len(node_ips))

  def test_GetAllNodeIps_FitOneRack(self):
    self.config.subnet.netmask = 26
    self.config.subnet.children.clear()
    self.cluster = ip.ClusterSubnet(self.config)

    # Subnet size can only fit aa rack
    node_ips = self.cluster.GetAllNodeIps()
    self.assertEqual(len(node_ips), 62)

    # Verifies no duplicate ip addresses are assigned to different nodes
    self.assertEqual(len(set([v for v in node_ips.values()])), len(node_ips))


if __name__ == "__main__":
    unittest.main()
