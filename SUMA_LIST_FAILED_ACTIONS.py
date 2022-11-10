#!/usr/bin/env python3
# Author : pankaj-kumar.goyal@hpe.com
# Purpose: List failed actions
# Usages:  python3 <script name.py>
# Pre-req: Python3 module "xmlrpclib" should be pre installed.
# Script Name: SUMA_LIST_FAILED_ACTIONS.py
from xmlrpc.client import ServerProxy
import ssl

def connect_suma(mgr_login = '', mgr_pass = ''):
    MANAGER_URL = "https://sample.com/rpc/api"
    MANAGER_LOGIN = mgr_login
    MANAGER_PASSWORD = mgr_pass
    # server SSL configuartion and your local SSL configuration
    context = ssl.create_default_context()
    client = ServerProxy(MANAGER_URL, context=context)
    key = client.auth.login(MANAGER_LOGIN, MANAGER_PASSWORD)
    return client, key
def list_failed_actions(client, key):
    try:
        res = client.schedule.listFailedActions(key)
        if res is None:
            print("INFO ! No action is listed in SUMA.")
        else:
            return res
            #return res[0].get('id')
    except Exception:
        print("ERROR! Action listing fail. Can't connect with SUSE manager.")    

def main():
    try:
        client, key = connect_suma() ## Generating session & session key
        response = list_failed_actions(client, key)
        print("\nList of actions are: ")
        print("***************************************************************************************************************************")
        print("ID          " + "NAME" + "                                              "+"CompletedSystems"+"      "+"FailedSystems"+"     "+"InProgressSystems")
        print("------------------------------------------------------------------------------------------------------------------------")
        if not len(response):
            print("There is no action marked as FAILED.")
        else:
            for val in response:
                print("{}   {}              {}                  {}                  {}".format(val['id'],val['name'],val['completedSystems'],val['failedSystems'],val['inProgressSystems']))
        #print(response[0]['id'])                                                                                                                                                                                                                                                                                                                                                                   
        print("*********************************************************************************************************************")
        client.auth.logout(key) ## Logout session with SUSE manager
    except Exception:
        print("ERROR! Check SUMA_LIST_FAILED_ACTIONS . Can't Fetch list of Failed actions.")
    
if __name__ == "__main__":
       main()
    
