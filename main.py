import proxmoxer
import requests
import yaml
import subprocess
import json
import pprint
import time
import argparse
from psycopg2 import connect as pg_connect
from initializator import initializator
from proxmox_connecter import proxmox_connector
from priority_management import set_priority, get_vm_by_priority, get_non_res
from get_node_status import get_node_status
from get_vm_status import get_vm_status
from disaster_counter import detect_disaster
import recovery_protocol


with open(r'./config.yml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

pg_client = pg_connect(host=config['db']['host'],
                        port=config['db']['port'],
                        user=config['db']['user'],
                        password=config['db']['pass'],
                        dbname=config['db']['database'])

parser = argparse.ArgumentParser(description='m_rogotnev diplom')
parser.add_argument('-v', action='store', help='vm table to set priority to')
parser.add_argument('-p', action='store', type=int, help='set priority. 1 - default. 0 - do not restore.')
parser.add_argument('-i', action='count', help='run initializator')

args = parser.parse_args()

### initializator
if args.i == 1:
    print("run initializator")
    initializator(config, pg_client)
    exit(0)

### set prioroty
if args.v is not None and args.p is not None and args.p >= 0:
    print(args.v)
    print(args.p)
    set_priority(pg_client, vm=args.v, priority=args.p)

### test get_vm_by_priority
# vm_list = get_vm_by_priority(pg_client)
#
# for vm in vm_list:
#     print(vm[0])


### main body
# while True:
#     proxmox = proxmox_connector(config, pg_client)
#     is_dead = detect_disaster(proxmox)
#     if is_dead is not None:
#         print("host is dead")
#         print(is_dead['node'])
#         recovery_protocol.mark_as_dead(dead_host=is_dead['node'], pg_client=pg_client)
#         recovery_list = []
#         priority_list = []
#         sorted_recovery_list = []
#         non_res_list = []
#         for vm in get_vm_by_priority(pg_client):
#             priority_list.append(vm[0])
#         for vm in get_non_res(pg_client):
#             non_res_list.append(vm[0])
#
#
#
#     get_node_status(config, pg_client, proxmox)
#     get_vm_status(config, pg_client, proxmox)
#     time.sleep(60)

print(recovery_protocol.extract_last_vm_data('autohost3', pg_client=pg_client))
