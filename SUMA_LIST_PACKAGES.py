#!/usr/bin/env python3
# install a package 

from xmlrpc.client import ServerProxy
import ssl
from datetime import datetime
import time
import xmlrpclib

MANAGER_URL = "https://sample.com/rpc/api"
MANAGER_LOGIN = ""
MANAGER_PASSWORD = ""
# You might need to set to set other options depending on your
# server SSL configuartion and your local SSL configuration
context = ssl.create_default_context()
client = ServerProxy(MANAGER_URL, context=context)
key = client.auth.login(MANAGER_LOGIN, MANAGER_PASSWORD)
package_list = client.packages.findByNvrea(key, 'rhnlib', '2.5.22', '9.el6', '', 'noarch')
today = datetime.today()
earliest_occurrence = xmlrpclib.DateTime(today)
client.system.schedulePackageInstall(key, 1000000001, package_list[0]['id'], earliest_occurrence)

client.auth.logout(key)


