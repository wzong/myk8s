import psutil
import re

from cluster.base import base_pb2

# Max rows per data center
_MAX_ROWS = 32
# Max num racks per row
_ROW_SIZE = 32
# Change to these parameters requires resetting all node since it impacts ips inference.
_RACK_SIZE = 64
# Max node_seq within a rack. Range [0..61].
# Reserving 63/64 for broadcast/network addr of potential subnet.
_MAX_NODE_SEQ = 61

class NodeId(object):
  """Unique ID for a L3 host.

  The format is `<2-letter cluster_id><2-letter rack_id><2 digit sequence number within rack>`
  The node can either be a machine or router.
    - Router's seq number is '00'
    - Machine's seq number is [01-62]
    - -1/63 is reserved for network/broadcast address in case subnet is needed (support up to /26)
  """

  def __init__(self, node_id: str or base_pb2.NodeId):
    self.cluster_id = ''
    self.rack_id = ''
    self.node_seq = 0

    # Unique seq number within a cluster.
    # - this is not global across all clusters
    # - not all ids are assignable, some ids are reserved for subnet's network/broadcast addresses
    self.rack_unique_seq = 0
    self.node_unique_seq = 0

    if type(node_id) is str:
      m = re.fullmatch(r'([a-z]{2})([a-z]{2})([0-9]{2})', node_id)
      if m:
        self.cluster_id = m.group(1)
        self.rack_id = m.group(2)
        self.node_seq = int(m.group(3).strip('0') or '0')
      else:
        raise ValueError('Invalid Node ID string: %s' % node_id)
    elif type(node_id) is base_pb2.NodeId:
      if not re.fullmatch(r'[a-z]{2}', node_id.cluster_id):
        raise ValueError('Invalid NodeId.cluster_id: %s' % node_id.cluster_id)
      if not re.fullmatch(r'[a-z]{2}', node_id.rack_id):
        raise ValueError('Invalid NodeId.rack_id: %s' % node_id.rack_id)
      self.cluster_id = node_id.cluster_id
      self.rack_id = node_id.rack_id
      self.node_seq = node_id.node_seq

    # Seq id range
    if self.node_seq < 0 or self.node_seq > _MAX_NODE_SEQ:
      raise ValueError('Invalid NodeId.node_seq: %d (range [0..%d])' % (
          self.node_seq, _MAX_NODE_SEQ))

    # Rack unique seq, 'aa' --> 0
    self.rack_unique_seq = _ROW_SIZE * (ord(self.rack_id[0]) - ord('a')) + (
        ord(self.rack_id[1]) - ord('a'))

    # Node unique seq, 'aa00' --> 0
    self.node_unique_seq = self.rack_unique_seq * _RACK_SIZE + self.node_seq

  def __str__(self):
    return '%s%s%s' % (self.cluster_id, self.rack_id, str(self.node_seq).zfill(2))

  def __add__(self, offset: int):
    node_unique_seq = self.node_unique_seq + offset
    node_seq = node_unique_seq % _RACK_SIZE
    rack_unique_seq = int(node_unique_seq / _RACK_SIZE)

    chr1 = chr(int(rack_unique_seq / _RACK_SIZE) + ord('a'))
    chr2 = chr(rack_unique_seq % _RACK_SIZE + ord('a'))
    if node_unique_seq < 0 or ord(chr1) > ord('z') or ord(chr2) > ord('z'):
      raise ValueError('NodeId out of bound %s + (%d)' % (self.__str__(), offset))
    node_id_pb = base_pb2.NodeId()
    node_id_pb.cluster_id = self.cluster_id
    node_id_pb.rack_id = chr1 + chr2
    node_id_pb.node_seq = node_seq
    return NodeId(node_id_pb)

  def __sub__(self, offset: int):
    return self.__add__(offset * -1)


class AbstractNode(object):
  """Abstraction of a node."""

  def __init__(self, node: base_pb2.Node):
    self.node_id = NodeId(node.node_id)
    self.node_type = node.node_type

  def GetNetworkAdapter(self, offset = 0) -> str:
    return 'eth%d' % offset

  def GetHeadScript(self) -> str:
    return '#!/bin/bash\n'

  def GetIpSetupScript(self, address: str) -> str:
    return '# IP SETUP SCRIPT: NOT IMPLEMENTED\n'

  def GetKubeadmScript(self) -> str:
    return '# Kubeadm SCRIPT: NOT IMPLEMENTED\n'
