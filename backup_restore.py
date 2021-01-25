from proxmoxer import ProxmoxAPI
import yaml
import re
from datetime import datetime
from pprint import pprint
from psycopg2 import connect as pg_connect


def get_new_vmid(pg_client):
    vm_id_next = 0
    pg_cursor = pg_client.cursor()
    pg_cursor.execute("SELECT id FROM vm_status")
    vm_id_list = pg_cursor.fetchall()
    for vm_id in vm_id_list:
        if vm_id[0] > vm_id_next:
            vm_id_next = vm_id[0]
    return vm_id_next + 1


def get_last_backup_archive(vm, node, proxmox):
    rec_node = proxmox.nodes(node)
    backups = rec_node.storage('Nas').content.get()
    last_backup = datetime(2000, 1, 1)
    last_backup_id = ""
    for backup in backups:
        if backup['vmid'] == vm:
            current_backup = datetime.strptime(re.search('Nas:backup/vzdump-qemu-%s-(.+?).vma.lzo' % vm, backup['volid']).group(1), '%Y_%m_%d-%H_%M_%S')
            if current_backup > last_backup:
                last_backup = current_backup
                last_backup_id = backup['volid']
    print("last backup id is %s" % last_backup_id)
    return last_backup_id


def restore_from_backup(node, archive, vmid, proxmox):
    restore = proxmox.nodes(node)
    restore.qemu.create(vmid=vmid, force=0, archive=archive)


# with open(r'./config.yml') as file:
#     config = yaml.load(file, Loader=yaml.FullLoader)

# proxmox = ProxmoxAPI(config['cluster']['host'], user=config['cluster']['user'],
#                      password=config['cluster']['pass'], verify_ssl=False)
#
# pg_client = pg_connect(host=config['db']['host'],
#                         port=config['db']['port'],
#                         user=config['db']['user'],
#                         password=config['db']['pass'],
#                         dbname=config['db']['database'])


# recovery_dict = {106: 'autohost2'}

# for key, value in recovery_dict.items():
#     restore_from_backup(node=value, archive=get_last_backup_archive(key, value, proxmox), pg_client=pg_client, vmid=get_new_vmid(pg_client))
