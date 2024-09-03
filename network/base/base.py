import psutil
import re

from network.base import base_pb2

# Change to these parameters requires resetting all node since it impacts ips inference.
_RACK_SIZE = 64


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

    self.rack_unique_seq = 0
    self.node_unique_seq = 0

    if type(node_id) is str:
      m = re.match(r'([a-z]{2})([a-z]{2})([0-9]{2})', node_id)
      if m:
        self.cluster_id = m.group(1)
        self.rack_id = m.group(2)
        self.node_seq = int(m.group(3).strip('0') or '0')
      else:
        raise ValueError('Invalid Node ID string: %s' % node_id)
    elif type(node_id) is base_pb2.NodeId:
      if not re.match(r'[a-z]{2}', node_id.cluster_id):
        raise ValueError('Invalid NodeId.cluster_id: %s' % node_id.cluster_id)
      if not re.match(r'[a-z]{2}', node_id.rack_id):
        raise ValueError('Invalid NodeId.rack_id: %s' % node_id.rack_id)
      if node_id.node_seq < 0 or node_id.node_seq >= (_RACK_SIZE - 1):
        raise ValueError('Invalid NodeId.node_seq: %d (max %d)' % (
            node_id.node_seq, _RACK_SIZE))
      self.cluster_id = node_id.cluster_id
      self.rack_id = node_id.rack_id
      self.node_seq = node_id.node_seq

    # Rack unique seq, 'aa' --> 0
    for c in self.rack_id:
      self.rack_unique_seq = self.rack_unique_seq * 10 + (ord(c) - ord('a'))

    # Node unique seq, 'aa00' --> 0
    self.node_unique_seq = self.rack_unique_seq * _RACK_SIZE + self.node_seq

  def __str__(self):
    return '%s%s%s' % (self.cluster_id, self.rack_id, str(self.node_seq).zfill(2))


class LocalNode(object):
  """This lib runs locally on a node."""

  def __init__(self, node_id: str or base_pb2.NodeId):
    self.node_id = NodeId(node_id)

  def GetNetIfAddress(self):
    return psutil.net_if_addrs()
