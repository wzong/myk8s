import json
import unittest

from google.protobuf import text_format
from network.base import base
from network.router import router
from network.router import router_pb2


_TEST_ROUTER = '''
  node_id { cluster_id: "mv", rack_id: "aa", node_seq: 0 }
  address: "10.2.0.1"
  subnet_mask: 16
  rack_ids: ["aa", "ab", "ba", "ca", "zz"]
  network_controller: "eth0"
'''

_TEST_NETPLAN = '''# Netplan eth0
network:
  ethernets:
    eth0:
      addresses:
      - 10.2.0.10/16
      dhcp4: false
      nameservers:
        addresses:
        - 8.8.8.8
        - 1.1.1.1
      routes:
      - to: default
        via: 10.2.0.1
  version: 2
'''

class BaseTest(unittest.TestCase):

  def setUp(self):
    self.r_pb = text_format.Parse(_TEST_ROUTER, router_pb2.Router())
    self.r = router.Router(self.r_pb)

  def test_Router_InvalidAddress(self):
    r_pb = self.r_pb
    r_pb.address = '10.3.0.2'
    r = router.Router(r_pb)

  def test_Router_InvalidNodeId(self):
    r_pb = self.r_pb

    r_pb.node_id.node_seq = 1
    with self.assertRaises(ValueError) as e:
      r = router.Router(r_pb)
    self.assertTrue('Invalid Router.node_id: node_seq' in str(e.exception))

    r_pb.node_id.node_seq = 0
    r_pb.node_id.rack_id = 'cc'
    with self.assertRaises(ValueError) as e:
      r = router.Router(r_pb)
    self.assertTrue('Invalid Router.node_id: rack out of router ip range' in str(e.exception))

  def test_GetNodeIp(self):
    self.assertEqual(self.r.GetNodeIp(base.NodeId('mvaa00')), '10.2.0.1')
    self.assertEqual(self.r.GetNodeIp(base.NodeId('mvaa01')), '10.2.0.2')
    self.assertEqual(self.r.GetNodeIp(base.NodeId('mvaa61')), '10.2.0.62')
    self.assertEqual(self.r.GetNodeIp(base.NodeId('mvab00')), '10.2.0.65')
    self.assertEqual(self.r.GetNodeIp(base.NodeId('mvba01')), '10.2.6.130')
    self.assertEqual(self.r.GetNodeIp(base.NodeId('mvca00')), '10.2.13.1')

  def test_GetNodeIp_NotSameCluster(self):
    with self.assertRaises(ValueError) as e:
      self.r.GetNodeIp(base.NodeId('xxaa01'))
    self.assertIn('is not in same cluster with router', str(e.exception))

  def test_GetNodeIp_NotConnected(self):
    with self.assertRaises(ValueError) as e:
      self.r.GetNodeIp(base.NodeId('mvxx01'))
    self.assertIn('is not connected to router', str(e.exception))

  def test_GetNodeIp_NotEnoughIp(self):
    r_pb = self.r_pb
    r_pb.subnet_mask = 24
    r = router.Router(r_pb)
    with self.assertRaises(ValueError) as e:
      r.GetNodeIp(base.NodeId('mvzz61'))
    self.assertIn('Unable to assign ip address for node', str(e.exception))

  def test_GetNodeNetplan(self):
    self.assertEqual(self.r.GetNodeNetplan(base.NodeId('mvaa09')), _TEST_NETPLAN)


if __name__ == "__main__":
    unittest.main()
