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


def get_non_res(pg_client):
    pg_cursor = pg_client.cursor()
    pg_cursor.execute("SELECT vm FROM vm_priority WHERE priority = 0 ORDER BY priority DESC")
    return pg_cursor.fetchall()
