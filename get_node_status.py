import yaml
from psycopg2 import connect as pg_connect
from proxmoxer import ProxmoxAPI
import pprint
import time


with open(r'./config.yml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)


pg_client = pg_connect(host=config['db']['host'],
                        port=config['db']['port'],
                        user=config['db']['user'],
                        password=config['db']['pass'],
                        dbname=config['db']['database'])

proxmox = ProxmoxAPI(config['cluster']['host'], user=config['cluster']['user'],
                     password=config['cluster']['pass'], verify_ssl=False)

# pprint.pprint(proxmox.cluster.resources.get(type='storage'))
# exit(0)

while True:
    pg_cursor = pg_client.cursor()
    pg_cursor.execute("DELETE FROM node_status")
    for node in proxmox.cluster.resources.get(type='node'):
        if node['status'] in 'online':
            node_max_cpu = node['maxcpu']
            node_max_ram = node['maxmem']
            node_max_disk = 0
            # находим максимальное место диска через жопу
            for storage in proxmox.cluster.resources.get(type='storage'):
                if storage['node'] in node['node'] and storage['storage'] in 'local-lvm':
                    node_max_disk = storage['maxdisk']

            node_cpu_reserved = 0
            node_ram_reserved = 0
            node_disk_reserved = 0

            print("node {node}".format(node=node['node']))
            for vm in proxmox.cluster.resources.get(type='vm'):
                if vm['node'] in node['node'] and vm['status'] in 'running':
#                    print("vm - {vm_name}\tcpu={vm_cpu}\tram={vm_ram}\tdisk={vm_disk}".format(vm_name=vm['name'], vm_cpu=vm['maxcpu'], vm_ram=vm['maxmem'],vm_disk=vm['maxdisk']))
                    node_cpu_reserved += int(vm['maxcpu'])
                    node_ram_reserved += int(vm['maxmem'])
                    node_disk_reserved += int(vm['maxdisk'])
#            print("max_cpu={cpu}\tmax_ram={ram}\tmax_disk={disk}".format(cpu=node_max_cpu, ram=node_max_ram, disk=node_max_disk))
#            print("reserved_cpu={cpu}\treserved_ram={ram}\treserved_disk={disk}".format(cpu=node_cpu_reserved, ram=node_ram_reserved, disk=node_disk_reserved))
            print("available_cpu={cpu}\tavailable_ram={ram}\tavailable_disk={disk}".format(cpu=node_max_cpu - node_cpu_reserved,
                                                                                           ram=node_max_ram - node_ram_reserved,
                                                                                           disk=node_max_disk - node_disk_reserved))
            avaliable_cpu = node_max_cpu - node_cpu_reserved
            avaliable_ram = (node_max_ram - node_ram_reserved) /1024/1024
            avaliable_disk = (node_max_disk - node_disk_reserved) /1024/1024
            sql_request = "INSERT INTO node_status VALUES (%s, %s, %s, %s);"
            data = (node['node'], avaliable_cpu, avaliable_ram, avaliable_disk)
            pg_cursor.execute(sql_request, data)
            pg_client.commit()

    time.sleep(30)
### available в базу
