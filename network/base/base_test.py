import json
import unittest

from network.base import base
from network.base import base_pb2


class NodeIdTest(unittest.TestCase):

  def test_NodeId_FromStr(self):
    node_id = base.NodeId('mvab12')
    self.assertEqual(node_id.cluster_id, 'mv')
    self.assertEqual(node_id.rack_id, 'ab')
    self.assertEqual(node_id.node_seq, 12)
    self.assertEqual(node_id.rack_unique_seq, 1)
    self.assertEqual(node_id.node_unique_seq, 76)

    node_id = base.NodeId('mvab00')
    self.assertEqual(node_id.node_seq, 0)
    self.assertEqual(node_id.node_unique_seq, 64)

  def test_NodeId_FromProto(self):
    node_id_pb = base_pb2.NodeId(cluster_id = 'mv', rack_id = 'ab', node_seq = 12)
    node_id = base.NodeId(node_id_pb)
    self.assertEqual(node_id.cluster_id, 'mv')
    self.assertEqual(node_id.rack_id, 'ab')
    self.assertEqual(node_id.node_seq, 12)
    self.assertEqual(node_id.rack_unique_seq, 1)
    self.assertEqual(node_id.node_unique_seq, 76)

  def test_NodeId_FromInvalidStr(self):
    with self.assertRaises(ValueError):
      base.NodeId('mvab0')
    with self.assertRaises(ValueError):
      base.NodeId('mva01')
    with self.assertRaises(ValueError):
      base.NodeId('mv01')
    with self.assertRaises(ValueError):
      base.NodeId('')

  def test_NodeId_FromInvalidProto(self):
    node_id_pb = base_pb2.NodeId(cluster_id = 'mv', rack_id = 'a', node_seq = 2)
    with self.assertRaises(ValueError):
      base.NodeId(node_id_pb)

    node_id_pb = base_pb2.NodeId(cluster_id = 'm', rack_id = 'ab', node_seq = 2)
    with self.assertRaises(ValueError):
      base.NodeId(node_id_pb)

    node_id_pb = base_pb2.NodeId(cluster_id = 'mv', rack_id = 'ab', node_seq = 62)
    with self.assertRaises(ValueError):
      base.NodeId(node_id_pb)

    node_id_pb = base_pb2.NodeId(cluster_id = 'mv', rack_id = 'ab', node_seq = -1)
    with self.assertRaises(ValueError):
      base.NodeId(node_id_pb)

  def testNodeId_ToString(self):
    node_id = base.NodeId('mvab12')
    self.assertEqual(str(node_id), 'mvab12')

  def testNodeId_Offset(self):
    node_id = base.NodeId('mvab12')
    self.assertEqual(str(node_id + 1), 'mvab13')
    self.assertEqual(str(node_id + 64), 'mvac12')
    self.assertEqual(str(node_id - 64), 'mvaa12')

  def testNodeId_OffsetOutOfBound(self):
    node_id = base.NodeId('mvaa00')
    with self.assertRaises(ValueError) as e:
      node_id + 26 * 26 * 64
    self.assertIn('NodeId out of bound', str(e.exception))
    with self.assertRaises(ValueError) as e:
      node_id - 1
    self.assertIn('NodeId out of bound', str(e.exception))

  def testNodeId_OffsetReserved(self):
    node_id = base.NodeId('mvaa00')
    with self.assertRaises(ValueError) as e:
      node_id + 62
    self.assertIn('Invalid NodeId.node_seq', str(e.exception))


class LocalNodeTest(unittest.TestCase):

  def test_LocalNode(self):
    self.assertNotEqual(None, base.LocalNode('mvab12').GetNetIfAddress())


if __name__ == "__main__":
    unittest.main()
