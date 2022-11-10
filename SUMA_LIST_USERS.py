#!/usr/bin/env python3
# Author : pankaj-kumar.goyal@hpe.com
# Purpose: This script will list user's name available on SUSE manager.
# Usages: python3 <script name.py>
# Pre-req: Python3 module "xmlrpclib" should be pre installed.
# Script Name: SUMA_LIST_USERS.py
from xmlrpc.client import ServerProxy
import ssl
MANAGER_URL = "https://sample.com/rpc/api"
MANAGER_LOGIN = ""
MANAGER_PASSWORD = ""
# You might need to set to set other options depending on your
# server SSL configuartion and your local SSL configuration
context = ssl.create_default_context()
client = ServerProxy(MANAGER_URL, context=context)
key = client.auth.login(MANAGER_LOGIN, MANAGER_PASSWORD)
user_list = client.user.list_users(key)
#print(client.user.list_users(key))
print("***************************")
print("List of SUSE Manager User: ")
print("***************************")
for user in user_list:
    print (user.get('login'))
print("***************************")
client.auth.logout(key)
