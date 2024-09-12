import re
import typing
import yaml

from ipcalc import ipcalc

from cluster.base import base
from cluster.base import base_pb2
from cluster.ip import ip_pb2


class Subnet(object):

  def __init__(self, config: ip_pb2.Subnet):
    self.address = config.address
    self.netmask = config.netmask
    self.gateways = config.gateways

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

  def GetIp(self, offset: str):
    """Returns the IP/subnet for the given index offset within the subnet."""
    return str(ipcalc.IP(int(self._network.host_first()) + offset))

  def GetSubnet(self, address: str):
    """Returns the subnet that the address belongs to, or None if not in the subnet."""
    result = None
    if address not in self._network:
      return None
    for child in self.children:
      subnet = child.GetSubnet(address)
      if subnet:
        return subnet
    if self.address == address:
      raise ValueError('Invalid IP address: cannot be network of subnet %s' % self)
    if self.broadcast == address:
      raise ValueError('Invalid IP address: cannot be broadcast of subnet %s' % self)
    return self

  def GetNetplan(self, address: str, network_adapter: str) -> str:
    subnet = self.GetSubnet(address)
    routes = [{'to': g.to, 'via': g.via} for g in subnet.gateways]
    netplan_config = {
      'network': {
        'ethernets': {
          network_adapter: {
            'dhcp4': False,
            'addresses': '%s/%d' % (address, subnet.netmask),
            'routes': routes,
            'nameservers': {
              'addresses': ['8.8.8.8', '1.1.1.1'],
            },
          }
        },
        'version': 2,
      }
    }
    return ('# Netplan %s\n' % network_adapter) + yaml.dump(
        netplan_config, default_flow_style=False)


class ClusterSubnet(object):

  def __init__(self, cluster_id: str, subnet: ip_pb2.Subnet):
    if not re.fullmatch(r'[a-z]{2}', cluster_id):
      raise ValueError('Invalid ClusterSubnet.cluster_id: %s' % cluster_id)
    self.cluster_id = cluster_id
    self.subnet = Subnet(subnet)
    self._node_ips = {}

  def CheckNode(self, node_id: base.NodeId):
    if str(node_id) in self._node_ips:
      return self._node_ips[str(node_id)]

    if node_id.cluster_id != self.cluster_id:
      raise ValueError('Node %s is not in cluster: %s' % (node_id, self.cluster_id))

    ip_offset = node_id.node_unique_seq
    if ip_offset < 0 or ip_offset >= self.subnet.size():
      raise ValueError('Unable to assign ip address for node %s, subnet %s/%d, offset %d' % (
          node_id, self.subnet.address, self.subnet, ip_offset))

  def GetNodeIp(self, node_id: base.NodeId) -> str:
    self.CheckNode(node_id)
    address = self.subnet.GetIp(node_id.node_unique_seq)
    subnet = self.subnet.GetSubnet(address)
    return '%s/%d' % (address, subnet.netmask)

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

  def GetNodeNetplan(self, node_id: base.NodeId, network_adapter: str) -> str:
    self.CheckNode(node_id)
    address = self.subnet.GetIp(node_id.node_unique_seq)
    return self.subnet.GetNetplan(address, network_adapter)
