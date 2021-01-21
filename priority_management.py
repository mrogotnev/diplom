import yaml
from psycopg2 import connect as pg_connect
import argparse


def set_priority(pg_client, vm, priority):
    pg_cursor = pg_client.cursor()
    pg_cursor.execute("DELETE FROM vm_priority WHERE vm='%s'" % vm)
    pg_client.commit()
    pg_cursor.execute("INSERT INTO vm_priority VALUES ('%s', '%i')" % (vm, priority))
    pg_client.commit()
    exit(0)


def get_vm_by_priority(pg_client):
    pg_cursor = pg_client.cursor()
    pg_cursor.execute("SELECT vm FROM vm_priority WHERE priority > 0 ORDER BY priority DESC")
    return pg_cursor.fetchall()


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

args = parser.parse_args()

if args.v is not None and args.p is not None and args.p >= 0:
    print(args.v)
    print(args.p)
    set_priority(pg_client, vm=args.v, priority=args.p)

vm_list = get_vm_by_priority(pg_client)

for vm in vm_list:
    print(vm[0])
