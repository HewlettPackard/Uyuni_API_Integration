#!/usr/bin/env python3
# Author : pankaj-kumar.goyal@hpe.com
# Purpose: Script will varify the server's OS patch status & will return a relevent message compliant/non-compliant. 
# Usages: python3 <script_name.py> <server_name> 
# Pre-req: Python3 module "xmlrpclib" should be pre installed.
# Script Name: SUMA_POST_PATCHING_COMP_STATUS.py

# Importing relevent modules
from xmlrpc.client import ServerProxy
# func -1, Setup RPC connection
def connect_suma(mgr_login = '', mgr_pass = ''):
    MANAGER_URL = "https://abc.com/rpc/api"
    MANAGER_LOGIN = mgr_login
    MANAGER_PASSWORD = mgr_pass
    # server SSL configuartion and your local SSL configuration
    context = ssl.create_default_context()
    client = ServerProxy(MANAGER_URL, context=context)
    key = client.auth.login(MANAGER_LOGIN, MANAGER_PASSWORD)
    return client, key
# func -2, Fetch out of date systems list from SUSE manager
def list_out_of_date_systems(client, key):
    try:
        res = client.system.listOutOfDateSystems(key)
        if res is None:
            print("INFO ! No outdated system listed in SUMA.")
        else:
            return res
    except Exception:
        print("ERROR-1! func list_out_of_date_systems().Check SUMA_LIST_COMPLIANT_SYSTEMS.py. Can't Fetch list of out-dated systems.")
# func -3, get server details
def check_system(client, key, systems):
    try:
        res = client.system.search.hostname(key, systems)
        if res is None:
            print("WARNING ! No such system found with name: " + systems)
        else:
            return res
    except Exception:
        print("ERROR! system check failed. Can't connect with SUSE manager.")
# Step -4, Main() function starts    
def main():
    try:
        # Check if required arguments has been passed at execution of script
        if ( len(sys.argv) != 2 ):
            print("Script need server name as an argument")
            exit(1)
        else:
            node = sys.argv[1]
        client, key = connect_suma() ## Generate session & session key
        response = list_out_of_date_systems(client, key)
        outdated = [] # Created list of out of dated systems.
        for i in response:
            outdated.append(i['name'].split('.')[0])
        node_detail = check_system(client, key, node)
        if node in outdated:
            print("non-compliant")
        elif len(node_detail):
            print("compliant")
        else:
            print("unknown")
                
    except Exception:
        print("ERROR-2 main() function! Check SUMA_POST_PATCHING_COMP_STATUS.py. Can't fetch systems patching status.")
    
if __name__ == "__main__":
       main()