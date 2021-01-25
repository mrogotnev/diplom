import yaml
import time
import argparse
from psycopg2 import connect as pg_connect
from initializator import initializator
from proxmox_connecter import proxmox_connector
from priority_management import set_priority
from get_node_status import get_node_status
from get_vm_status import get_vm_status
from disaster_counter import detect_disaster
import recovery_protocol
from backup_restore import restore_from_backup, get_last_backup_archive, get_new_vmid


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

### main body
while True:
    proxmox = proxmox_connector(config, pg_client)
    is_dead = detect_disaster(proxmox, pg_client)
    if is_dead is not None:
        print("host is dead")
        print(is_dead['node'])
        recovery_protocol.mark_as_dead(dead_host=is_dead['node'], pg_client=pg_client)
        recovery_dict = recovery_protocol.extract_last_vm_data(pg_client, dead_host=is_dead['node'])
        available_res = recovery_protocol.extract_available_resources_data(pg_client, dead_host=is_dead['node'])
        vm_to_transfer = recovery_protocol.get_vm_to_transfer(vm_from_dead_node=recovery_dict, available_resources=available_res)
        print("debug")
        print(vm_to_transfer)
        restore_count = 0
        for key, value in vm_to_transfer.items():
            print("restoring %s on %s" % (key, value))
            restore_from_backup(node=value, archive=get_last_backup_archive(key, value, proxmox), vmid=get_new_vmid(pg_client) + restore_count, proxmox=proxmox)
            restore_count += 1

    get_node_status(config, pg_client, proxmox)
    get_vm_status(config, pg_client, proxmox)
    time.sleep(60)


#print(get_vm_by_priority(pg_client, 'autohost2'))
#print(recovery_protocol.extract_last_vm_data(pg_client, 'autohost2'))
# recovery_dict = recovery_protocol.extract_last_vm_data(pg_client, dead_host='autohost2')
# print(recovery_dict)
# available_res = recovery_protocol.extract_available_resources_data(pg_client, dead_host='autohost2')
# vm_to_transfer = recovery_protocol.get_vm_to_transfer(vm_from_dead_node=recovery_dict,
#                                                       available_resources=available_res)
#
# print(vm_to_transfer)
