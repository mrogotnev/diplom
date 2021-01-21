import proxmoxer
import requests
import yaml
import subprocess
import json
import pprint
import time


with open(r'./config.yml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

from proxmoxer import ProxmoxAPI
proxmox = ProxmoxAPI(config['cluster']['host'], user=config['cluster']['user'],
                     password=config['cluster']['pass'], verify_ssl=False)

