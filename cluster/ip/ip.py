import re
import typing

from ipcalc import ipcalc

from cluster.base import base
from cluster.base import base_pb2
from cluster.ip import ip_pb2


class Subnet(object):

  def __init__(self, config: ip_pb2.ClusterSubnet):
    self.address = config.address
    self.netmask = config.netmask

    self._network = ipcalc.Network('%s/%d' % (self.address, self.netmask))
    if self.address != self._network.network():
      raise ValueError(
          'Invalid Subnet.address: network address must be 0th addr in the subnet, '
          'got %s expect %s' % (self.address, self._network.network()))
    if self._network.size() < 64:
      raise ValueError('Minimum subnet size is 64 (netmask: 26)')

    self.broadcast = self._network.broadcast()
    self.children = []
    for s in config.children:
      child = Subnet(s)
      if child.address not in self._network or child.netmask <= self.netmask:
        raise ValueError(
            'Invalid Subnet.address: not a child subnet, '
            'parent %s, child %s' % (self, child))
      self.children.append(child)

  def __str__(self) -> str:
    return str(self._network)

  def size(self) -> int:
    return self._network.size()

  def GetIpAddress(self, offset: str) -> str:
    """Returns the IP/netmask for the given index offset within the subnet."""
    address = str(ipcalc.IP(int(self._network.host_first()) + offset))
    subnet = self.GetSubnet(address)
    if subnet.address == address:
      raise ValueError('Invalid IP address: cannot be network of subnet %s' % self)
    if subnet.broadcast == address:
      raise ValueError('Invalid IP address: cannot be broadcast of subnet %s' % self)
    return '%s/%d' % (address, subnet.netmask)

  def GetSubnet(self, address: str):
    """Returns the subnet that the address belongs to, or None if not in the subnet."""
    if address not in self._network:
      return None
    for child in self.children:
      subnet = child.GetSubnet(address)
      if subnet:
        return subnet
    return self


class ClusterSubnet(object):

  def __init__(self, config: ip_pb2.ClusterSubnet):
    if not re.fullmatch(r'[a-z]{2}', config.cluster_id):
      raise ValueError('Invalid ClusterSubnet.cluster_id: %s' % config.cluster_id)
    self.cluster_id = config.cluster_id
    self.subnet = Subnet(config.subnet)
    self._node_ips = {}

  def GetNodeIp(self, node_id: base.NodeId) -> str:
    if str(node_id) in self._node_ips:
      return self._node_ips[str(node_id)]

    if node_id.cluster_id != self.cluster_id:
      raise ValueError('Node %s is not in cluster: %s' % (node_id, self.cluster_id))

    ip_offset = node_id.node_unique_seq
    if ip_offset < 0 or ip_offset >= self.subnet.size():
      raise ValueError('Unable to assign ip address for node %s, subnet %s/%d, offset %d' % (
          node_id, self.router_pb.address, self.subnet, ip_offset))
    # Offset 0 is the network address and should be skipped
    return self.subnet.GetIpAddress(ip_offset)

  def GetAllNodeIps(self) -> typing.Dict[str, str]:
    if self._node_ips:
      return self._node_ips

    for i in range(26):
      for j in range(26):
        for k in range(62):
          node_id = base.NodeId(base_pb2.NodeId(
              cluster_id = 'mv',
              rack_id = chr(ord('a') + i) + chr(ord('a') + j),
              node_seq = k))
          if node_id.node_unique_seq >= self.subnet.size():
            return self._node_ips
          self._node_ips[str(node_id)] = self.GetNodeIp(node_id)
    return self._node_ips
