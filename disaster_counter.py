from proxmoxer import ProxmoxAPI
import yaml
import time
from recovery_protocol import if_alive


def counter(sus_node, disaster_count, proxmox):
    if get_node_status(get_nodes(proxmox), sus_node) != 'online':
        disaster_count += 1
        print("disaster count: %s" % disaster_count)
        if disaster_count > 2:
            return True
        else:
            time.sleep(30)
            return counter(sus_node, disaster_count, proxmox)


def get_nodes(proxmox):
    return proxmox.cluster.resources.get(type='node')


def get_node_status(nodes, target_node):
    for node in nodes:
        if node['node'] in target_node:
            return node['status']


# with open(r'./config.yml') as file:
#     config = yaml.load(file, Loader=yaml.FullLoader)
#
#
# proxmox = ProxmoxAPI(config['cluster']['host'], user=config['cluster']['user'],
#                      password=config['cluster']['pass'], verify_ssl=False)

def detect_disaster(proxmox, pg_client):
    for node in get_nodes(proxmox):
        if node['status'] != 'online' and if_alive(pg_client, node['node']):
            print("not responding: " + node['node'])
            is_dead = counter(node['node'], 1, proxmox)
            if is_dead is True:
                return(node)
    print("all good")
