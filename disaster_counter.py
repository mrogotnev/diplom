from proxmoxer import ProxmoxAPI
import yaml
import time


def counter(sus_node, disaster_count):
    if get_node_status(get_nodes(proxmox), sus_node) != 'online':
        disaster_count += 1
        print("disaster count: %s" % disaster_count)
        if disaster_count > 10:
            print("alarm")
        else:
            time.sleep(30)
            counter(sus_node, disaster_count)


def get_nodes(proxmox):
    return proxmox.cluster.resources.get(type='node')


def get_node_status(nodes, target_node):
    for node in nodes:
        if node['node'] in target_node:
            return node['status']


with open(r'./config.yml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)


proxmox = ProxmoxAPI(config['cluster']['host'], user=config['cluster']['user'],
                     password=config['cluster']['pass'], verify_ssl=False)

while True:
    for node in get_nodes(proxmox):
        if node['status'] != 'online':
            print("not responding: " + node['node'])
            counter(node['node'], 1)
    print("all good")
    time.sleep(30)
