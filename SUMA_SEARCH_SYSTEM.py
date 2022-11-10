#!/usr/bin/env python3
# Author : pankaj-kumar.goyal@hpe.com
# Purpose: Script will fetch details of a systems from SUMA. 
# Usages: python3 <script_name.py> system 
# Pre-req: Python3 module "xmlrpclib" should be pre installed.
# Script Name: SUMA_SEARCH_SYSTEM.py

# Step -0, Importing relevent modules
import ssl, sys, smtplib, csv, os
from xmlrpc.client import ServerProxy
from string import Template
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase 
from email import encoders
# Step -1, Setup RPC connection
def connect_suma(mgr_login = '', mgr_pass = ''):
    MANAGER_URL = "https://sample.com/rpc/api"
    MANAGER_LOGIN = mgr_login
    MANAGER_PASSWORD = mgr_pass
    # server SSL configuartion and your local SSL configuration
    context = ssl.create_default_context()
    client = ServerProxy(MANAGER_URL, context=context)
    key = client.auth.login(MANAGER_LOGIN, MANAGER_PASSWORD)
    return client, key

def check_system(client, key, systems):
    try:
        res = client.system.search.hostname(key, systems)
        if res is None:
            print("WARNING ! No such system found with name: " + systems)
        else:
            return res
    except Exception:
        print("ERROR! system check failed. Can't connect with SUSE manager.")
    
def main():
    try:
        if ( len(sys.argv) != 2 ):
            print("Script need comma seperated list of servers as an argument")
            exit(1)
        else:
            client, key = connect_suma() ## Generate session & session key
            response = check_system(client, key, sys.argv[1])
            print (response)
    except Exception:
        print("ERROR-2 main() function! Check SUMA_SEARCH_SYSTEM.py. Can't check system details.")
    
if __name__ == "__main__":
       main()
