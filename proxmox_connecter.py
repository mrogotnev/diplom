from proxmoxer import ProxmoxAPI
import yaml
from psycopg2 import connect as pg_connect


def is_available(pg_client, hostname):
    pg_cursor = pg_client.cursor()
    pg_cursor.execute("SELECT available FROM available_nodes WHERE nodename = '%s'" % hostname)
    return pg_cursor.fetchone()[0]


# with open(r'./config.yml') as file:
#     config = yaml.load(file, Loader=yaml.FullLoader)
#
# pg_client = pg_connect(host=config['db']['host'],
#                         port=config['db']['port'],
#                         user=config['db']['user'],
#                         password=config['db']['pass'],
#                         dbname=config['db']['database'])

def proxmox_connector(config, pg_client):
    for host in config['cluster']['host']:
        print(host)
        if is_available(pg_client, host):
            try:
                proxmox = ProxmoxAPI(config['cluster']['host'][host], user=config['cluster']['user'],
                                     password=config['cluster']['pass'], verify_ssl=False)
                print("connected to " + host)
                return proxmox
            except Exception:
                print("host %s unavailable" % host)
