import yaml
from psycopg2 import connect as pg_connect
from proxmoxer import ProxmoxAPI
import pprint
import time


# with open(r'./config.yml') as file:
#     config = yaml.load(file, Loader=yaml.FullLoader)
#
#
# pg_client = pg_connect(host=config['db']['host'],
#                         port=config['db']['port'],
#                         user=config['db']['user'],
#                         password=config['db']['pass'],
#                         dbname=config['db']['database'])
#
# proxmox = ProxmoxAPI(config['cluster']['host'], user=config['cluster']['user'],
#                      password=config['cluster']['pass'], verify_ssl=False)

#pprint.pprint(proxmox.cluster.resources.get(type='vm'))

def get_vm_status(config, pg_client, proxmox):
    pg_cursor = pg_client.cursor()
    pg_cursor.execute("DELETE FROM vm_status")
    for vm in proxmox.cluster.resources.get(type='vm'):
        print(vm)

        if vm['status'] in 'running':
            print("name - {name}\t"
                  "id - {id}\t"
                  "node - {node}\t"
                  "cpu - {cpu}\t"
                  "ram - {ram}\t"
                  "disk - {disk}".format(name=vm['name'], id=vm['vmid'], node=vm['node'], cpu=vm['maxcpu'], ram=vm['maxmem'], disk=vm['maxdisk']))

            sql_request = "INSERT INTO vm_status VALUES (%s, %s, %s, %s, %s, %s);"
            data = (vm['name'], vm['vmid'], vm['node'], int(vm['cpu'] * 100), vm['maxmem'] /1024/1024 , vm['maxdisk'] /1024/1024, )
            pg_cursor.execute(sql_request, data)

        #pg_cursor.execute(sql_request)
        pg_client.commit()
