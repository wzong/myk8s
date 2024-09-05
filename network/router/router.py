from ipcalc import ipcalc
import yaml

from network.base import base
from network.base import base_pb2
from network.router import router_pb2


class Router(object):

  def __init__(self, router_pb: router_pb2.Router):
    self.router_pb = router_pb
    self.node_id = base.NodeId(router_pb.node_id)
    if self.node_id.node_seq != 0:
      raise ValueError('Invalid Router.node_id: node_seq must be 0, got %s' % self.node_id)
    for rack_id in router_pb.rack_ids:
      if self.node_id.rack_id > rack_id:
        raise ValueError('Invalid Router.node_id: rack out of router ip range, rack %s, router %s'
            % (rack_id, self.node_id))

  def _ValidateNodeId(self, node_id: base.NodeId) -> base.NodeId:
    if node_id.cluster_id != self.node_id.cluster_id:
      raise ValueError('Node %s is not in same cluster with router: %s' % (node_id, self.node_id))
    if node_id.rack_id not in self.router_pb.rack_ids:
      raise ValueError('Node %s is not connected to router: %s' % (node_id, self.node_id))
    return node_id

  def GetNodeIp(self, node_id: base.NodeId) -> str:
    self._ValidateNodeId(node_id)
    network = ipcalc.Network('%s/%d' % (self.router_pb.address, self.router_pb.subnet_mask))
    ip_offset = node_id.node_unique_seq
    if ip_offset < 0 or ip_offset >= network.size():
      raise ValueError('Unable to assign ip address for node %s, subnet %s/%d, offset %d' % (
          node_id, self.router_pb.address, self.router_pb.subnet_mask, ip_offset))
    return str(network[ip_offset])

  def GetNodeNetplan(self, base.NodeId) -> str:
    ip_address = self.GetNodeIp(node_id)
    ip_mask = self.router_pb.subnet_mask
    network_controller = self.router_pb.network_controller
    netplan_config = {
      'network': {
        'ethernets': {
          network_controller: {
            'dhcp4': False,
            'addresses': ['%s/%d' % (ip_address, ip_mask)],
            'routes': [{
              'to': 'default',
              'via': self.router_pb.address,
            }],
            'nameservers': {
              'addresses': ['8.8.8.8', '1.1.1.1'],
            },
          }
        },
        'version': 2,
      }
    }
    return ('# Netplan %s\n' % network_controller) + yaml.dump(
        netplan_config, default_flow_style=False)
