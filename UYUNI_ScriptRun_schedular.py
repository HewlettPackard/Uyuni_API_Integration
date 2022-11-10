#!/usr/bin/env python3
# Author : pankaj-kumar.goyal@hpe.com
# Purpose: To push a server patching schedule on SUSE manager. Script will accept "list of server" & "schedule" as
#          an arguments with script.  Script will schedule a action of servers in batch of 10 and will distribute each batch within 15 minutes of timeframe
# Usages: This script will accept three arguments in format: <server1,server2,server3> <YYYY:MM:DD> <HH:MM>
#         so here the sample to run: 
#           <script_name.py> <server1,server2,server3> <YYYY:MM:DD> <HH:MM>
# Pre-req: Script should be run with "root". Python3 module "iso8601" & "xmlrpclib" should be pre installed.
# Script Name: UYUNI_ScriptRun_schedular.py
# created on 27-Jun-2022

# Import respective modules & fucntions
from logging import root
from xmlrpc.client import ServerProxy
import ssl, sys, random
from datetime import datetime, timezone
import time, iso8601  # iso8601 module need install via pip

# Step -1, Setup RPC connection and generate session key
def connect_suma(mgr_login = '', mgr_pass = ''):
    MANAGER_URL = "https://sample.com/rpc/api"
    MANAGER_LOGIN = mgr_login
    MANAGER_PASSWORD = mgr_pass
    # server SSL configuartion and your local SSL configuration
    context = ssl.create_default_context()
    client = ServerProxy(MANAGER_URL, context=context)
    key = client.auth.login(MANAGER_LOGIN, MANAGER_PASSWORD)
    return client, key
# Step- 2, check if server exist in SUMA or Uyuni

def check_system(client, key, systems):
    try:
        #client, key = connect_suma()
        res = client.system.search.hostname(key, systems)
        return res
    except Exception:
        print("WARNING ! No such system found with name: {} ".format(systems))
        
# Step -3  Schedule script run action for batch of servers.
def schedule_script(client, key, slabel, sids, b_script, sch, hosts_list):
    try:
        #client, key = connect_suma()
        schd = iso8601.parse_date(sch)
        res = client.system.scheduleScriptRun(key, slabel, sids, 'root', 'root', 600, b_script, schd)
        if res is None:
            print("NOTIFICATION ! There is an error in scheduleScriptRun function")
        else:
            print("Linux OS Patching script scheduled with action ID: {} for systems: {}".format(res,hosts_list))
            #return res
    except Exception:
        print("ERROR! Check schedule script function.")
    
# Step -4 date and time calculation 
def cal_slicing(str1):
    val = str1.split(':')
    year = int(val[0])
    month = int(val[1])
    mdate = int(val[2])
    return year, month, mdate 
# Step -5 date and time calculation    
def time_slicing(str2):
    hh = int(str2.split(':')[0])
    mm = int(str2.split(':')[1])
    return hh, mm
# Step -6 Split the list into group of 10 servers
def split(list_a, batch_size):
    
  for i in range(0, len(list_a), batch_size):
    yield list_a[i:i + batch_size]
# Step -7 Main function call 
def main():
    try:
        message = """This script need 3 arguments in respetive order i.e. <script_name.py> <server1,server2,server3> <YYYY:MM:DD> <HH:MM>
            1) list of (",") seperated nodes list for example: "server1,server2,server3".
            2) For schedule year, month, date in YYYY:MM:DD format.
            3) For schedule hours & minute in HH:MM format. """
        
        if (len(sys.argv) < 4 or len(sys.argv) > 4):
            print("Error ! There is a mismatch in required number of arguments \n")
            print(message + "\n")
            sys.exit(1)
        else:
            client, key = connect_suma() ## Generating session & session key
            systems_name = sys.argv[1].split(',')
            year, month, mdate  = cal_slicing(sys.argv[2])
            hh, mm = time_slicing(sys.argv[3])
            slabel = "Linux-OS-Patching"
            systems_list = []
            host_fqdn = []
            for host in systems_name:
                sid = check_system(client, key, host)
                if not len(sid):
                    print("NOTIFICATION !! Host {} is not available in SUSE Manager or Uyuni.".format(host))
                    pass
                else:
                    systems_list.append(sid[0].get('id'))
                    host_fqdn.append(sid[0].get('hostname'))
            run_script = """\
                #!/bin/bash
                curl -Sks https://sample.com/pub/scripts/patch/do_patch.sh | bash -s init
                """
            if not len(systems_list):
                pass
            else:
                                
                if (len(systems_list) < 10):
                    batch_size = len(systems_list)
                else:
                    batch_size = 10           
                new_list = list(split(systems_list, batch_size))
                new_fqdn = list(split(host_fqdn, batch_size))
                mins = 0
                for i in range(len(new_list)):
                    
                    schedule = datetime(year, month, mdate, hh, mins, tzinfo=timezone.utc).isoformat()
                    schedule_script(client, key, slabel, new_list[i], run_script, schedule, new_fqdn[i])    
                    if (mins < 16):
                        mins = mins + 2
                    else: 
                        mins = 0
            client.auth.logout(key) ## Logout session with SUSE manager       
        
    except Exception:
        print ("ERROR! Can't schedule ScriptRun. There is an error exception in main() function.")
    
if __name__ == "__main__":
       main()
       