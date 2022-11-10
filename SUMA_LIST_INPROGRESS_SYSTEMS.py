#!/usr/bin/env python3
# Author : pankaj-kumar.goyal@hpe.com
# Purpose: Returns a list of systems that have a specific action in progress.
# Usages:  python3 <script name.py> <action ID or comma seperated List of action IDs>
# Pre-req: Python3 module "xmlrpclib" should be pre installed.
# Script Name: SUMA_LIST_INPROGRESS_SYSTEMS.py
from xmlrpc.client import ServerProxy
import ssl, sys

def connect_suma(mgr_login = '', mgr_pass = ''):
    MANAGER_URL = "https://sample.com/rpc/api"
    MANAGER_LOGIN = mgr_login
    MANAGER_PASSWORD = mgr_pass
    # server SSL configuartion and your local SSL configuration
    context = ssl.create_default_context()
    client = ServerProxy(MANAGER_URL, context=context)
    key = client.auth.login(MANAGER_LOGIN, MANAGER_PASSWORD)
    return client, key
def list_inprogress_systems(client, key, aid):
    try:
        res = client.schedule.listInProgressSystems(key, aid)
        #print (res)
        if res is None:
            print("INFO ! No system is listed for action ID: %s" % aid)
        else:
            return res
    except Exception:
        print("ERROR! Valid action ID has not been provided.")    

def main():
    try:
        client, key = connect_suma() ## Generating session & session key
        action_ids = sys.argv[1].split(',')
        print("\nList of In-Progress Systems are: ")
        print("************************************************************************************")
        print("SERVER NAME                      " + "MESSAGE")
        print("------------------------------------------------------------------------------------")

        for aid in action_ids:
            #print(aid)
            response = list_inprogress_systems(client, key, int(aid))
            if response is None:
                print("INFO ! No system is listed for action ID: %s" % aid)
            else:
                #print(response)
                print("{}      {}".format(response[0]['server_name'],response[0]['message']))
        print("************************************************************************************")
        client.auth.logout(key) ## Logout session with SUSE manager
    except Exception:
        print("ERROR! Check script SUMA_LIST_INPROGRESS_SYSTEMS . Can't Fetch list of In-Progress Systems.")
    
if __name__ == "__main__":
       main()