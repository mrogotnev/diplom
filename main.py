import proxmoxer
import requests
import yaml
import subprocess
import json
import pprint
import time

with open(r'./config.yml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

from proxmoxer import ProxmoxAPI
proxmox = ProxmoxAPI(config['cluster']['host'], user=config['cluster']['user'],
                     password=config['cluster']['pass'], verify_ssl=False)

pprint.pprint(proxmox.cluster.resources.get(type='vm'))
# while True:
#     nodes_dict = proxmox.nodes.get()
#     for node in nodes_dict:
#         print(proxmox.nodes(node['node']).openvz.get())
#         exit(0)
#         node_vm_dict = proxmox.nodes(node['node']).openvz.get()
#         pprint.pprint(node_vm_dict)
#         if node['status'] != 'online':
#             print('alert!')
#             print("node %s is not online!" % node['id'])
#     time.sleep(60)

##pprint.pprint(proxmox.cluster.resources.get(type='vm'))

### archive: Nas:backup/vzdump-qemu-100-2020_12_14-21_38_47.vma.lzo

# node = proxmox.nodes('autohost2')
# node.qemu.create(vmid=101, force=0,
#                  archive='Nas:backup/vzdump-qemu-100-2020_12_14-21_38_47.vma.lzo')
#
