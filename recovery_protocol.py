from proxmoxer import ProxmoxAPI
import yaml
from psycopg2 import connect as pg_connect
import time
import pprint


def mark_as_dead(dead_host, pg_client):
    pg_cursor = pg_client.cursor()
    pg_cursor.execute("UPDATE available_nodes SET available = False WHERE nodename = '%s'" % dead_host)
    pg_client.commit()

def if_alive(pg_client, node):
    pg_cursor = pg_client.cursor()
    pg_cursor.execute("SELECT available FROM available_nodes WHERE nodename = '%s'" % node)
    return bool(pg_cursor.fetchone()[0])


def extract_last_vm_data(pg_client, dead_host):
    pg_cursor = pg_client.cursor()
    vm_dict = {}
    pg_cursor.execute("SELECT s.*, CASE WHEN p.priority is NULL THEN 1 ELSE p.priority END FROM vm_status s INNER JOIN vm_priority p ON s.vm_name = p.vm WHERE node_name = '%s' AND p.priority > 0 ORDER BY priority DESC;" % dead_host)
    vm_from_dead_node = pg_cursor.fetchall()
    for vm in vm_from_dead_node:
        vm_dict[vm[0]] = {}
        vm_dict[vm[0]]['id'] = vm[1]
        vm_dict[vm[0]]['cpu'] = vm[3]
        vm_dict[vm[0]]['ram'] = vm[4]
        vm_dict[vm[0]]['disk'] = vm[5]
    return vm_dict


def extract_available_resources_data(pg_client, dead_host):
    pg_cursor = pg_client.cursor()
    available_resources_dict = {}
    pg_cursor.execute("SELECT * FROM node_status WHERE node != '%s';" % dead_host)
    available_resources_on_nodes = pg_cursor.fetchall()
    for node in available_resources_on_nodes:
        available_resources_dict[node[0]] = {}
        available_resources_dict[node[0]]['cpu'] = node[1]
        available_resources_dict[node[0]]['ram'] = node[2]
        available_resources_dict[node[0]]['disk'] = node[3]
    return available_resources_dict


# dead_host = "autohost3"

# with open(r'./config.yml') as file:
#     config = yaml.load(file, Loader=yaml.FullLoader)
#
# pg_client = pg_connect(host=config['db']['host'],
#                         port=config['db']['port'],
#                         user=config['db']['user'],
#                         password=config['db']['pass'],
#                         dbname=config['db']['database'])
#
# proxmox = ProxmoxAPI(config['cluster']['host'], user=config['cluster']['user'],
#                      password=config['cluster']['pass'], verify_ssl=False)
#
# mark_as_dead(dead_host, pg_client)
#
# vm_from_dead_node = extract_last_vm_data(dead_host, pg_client)

#vm_from_dead_node_sorted = sort_by_priority(vm_from_dead_node)

#print(vm_from_dead_node)
# available_resources = extract_available_resources_data(dead_host, pg_client)
# #print(available_resources)
#
# vm_to_transfer = {}
# vm_saved = []
#
def get_vm_to_transfer(vm_from_dead_node, available_resources):
    vm_to_transfer = {}
    for vm in vm_from_dead_node:
        for available_node in available_resources:
            if available_resources[available_node]['cpu'] - vm_from_dead_node[vm]['cpu'] > 0 and available_resources[available_node]['ram'] - vm_from_dead_node[vm]['ram'] > 0 and available_resources[available_node]['disk'] - vm_from_dead_node[vm]['disk'] > 0:
                print("we will transfer %s on %s" % (vm, available_node))
                print("%s\t cpu - %s\t ram - %s\t disk - %s" % (vm, vm_from_dead_node[vm]['cpu'], vm_from_dead_node[vm]['ram'], vm_from_dead_node[vm]['disk']))
                print("%s\t cpu - %s\t ram - %s\t disk - %s" % (available_node, available_resources[available_node]['cpu'], available_resources[available_node]['ram'], available_resources[available_node]['disk']))
                vm_to_transfer[vm_from_dead_node[vm]['id']] = available_node
                available_resources[available_node]['cpu'] = available_resources[available_node]['cpu'] - vm_from_dead_node[vm]['cpu']
                available_resources[available_node]['ram'] = available_resources[available_node]['ram'] - vm_from_dead_node[vm]['ram']
                available_resources[available_node]['disk'] = available_resources[available_node]['disk'] - vm_from_dead_node[vm]['disk']
                break
    return vm_to_transfer
#                vm_saved.append(vm)
#
# ### send to backup restore
# print(vm_to_transfer)
#
# for vm in vm_saved:
#     vm_from_dead_node.pop(vm)
#
# ### send to email
# pprint.pprint(vm_from_dead_node)
