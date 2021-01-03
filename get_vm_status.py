import yaml
from psycopg2 import connect as pg_connect
from proxmoxer import ProxmoxAPI
import pprint
import time


with open(r'./config.yml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)


# pg_client = pg_connect(host=config['db']['host'],
#                        port=config['db']['port'],
#                        user=config['db']['user'],
#                        password=config['db']['pass'],
#                        dbname=config['db']['database'])

proxmox = ProxmoxAPI(config['cluster']['host'], user=config['cluster']['user'],
                     password=config['cluster']['pass'], verify_ssl=False)

#pprint.pprint(proxmox.cluster.resources.get(type='vm'))

while True:
    for vm in proxmox.cluster.resources.get(type='vm'):
    ### удалить из базы старое говно
    ### это говно в базу

    ### читай про курсор
    ### вот пример
    # pg_cursor = pg_client.cursor()
    # sql_request = "SELECT (extract(epoch from now()) - extract(epoch from max(({col})))) / 60 FROM {tbl}".format(
    #     col=config[database_name]['monitoring'][i]['column'],
    #     tbl=config[database_name]['monitoring'][i]['table'])
    # pg_cursor.execute(sql_request)
    # time_diff_minutes = pg_cursor.fetchone()[0]

        if vm['status'] in 'running':
            print("name - {name}\t"
                  "id - {id}\t"
                  "node - {node}\t"
                  "cpu - {cpu}\t"
                  "ram - {ram}\t"
                  "disk - {disk}".format(name=vm['name'], id=vm['vmid'], node=vm['node'], cpu=vm['maxcpu'], ram=vm['maxmem'], disk=vm['maxdisk']))
    time.sleep(30)
