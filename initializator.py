import yaml
from psycopg2 import connect as pg_connect
from proxmoxer import ProxmoxAPI


with open(r'./config.yml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

pg_client = pg_connect(host=config['db']['host'],
                        port=config['db']['port'],
                        user=config['db']['user'],
                        password=config['db']['pass'],
                        dbname=config['db']['database'])

pg_cursor = pg_client.cursor()


for host in config['cluster']['host_new']:
    print(host)
    try:
        proxmox = ProxmoxAPI(config['cluster']['host_new'][host], user=config['cluster']['user'],
                             password=config['cluster']['pass'], verify_ssl=False)
    except Exception:
        print(Exception)
        print("host %s unavailable" % host)
        print("check config files, please")
        exit(1)

pg_cursor.execute("DELETE FROM available_nodes")

for node in proxmox.cluster.resources.get(type='node'):
    pg_cursor.execute("INSERT INTO available_nodes VALUES ('%s', '%s', True)" % (node['node'], config['cluster']['host_new'][node['node']]))
    pg_client.commit()

print("all nodes initialized")
