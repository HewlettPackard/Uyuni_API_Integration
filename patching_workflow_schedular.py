#!/usr/bin/env python3
# Author : pankaj-kumar.goyal@hpe.com
# Purpose: To push a server patching schedule on SUSE manager. Script will accept "list of server" & "schedule" as
#          an arguments with script. 
# Usages: This script will accept three arguments in format: <server1,server2,server3> <YYYY:MM:DD> <HH:MM>
#         so here the sample to run: 
#           <script_name.py> <server1,server2,server3> <YYYY:MM:DD> <HH:MM>
# Pre-req: Script should be run with "root". Python3 module "iso8601" & "xmlrpclib" should be pre installed.
# Script Name: patching_workflow_schedular.py

# Import respective modules & fucntions
from xmlrpc.client import ServerProxy
import ssl, sys
from datetime import datetime, timezone
import time, iso8601  # iso8601 module need install via pip

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
# Step- 2, Create an action chain
def actionchain(client, key, chain_name):
    res = client.actionchain.createChain(key,chain_name)
    return res

# Step- 3, input list of servers to be patched and check if its registered on Uyuni. If not registered, raise flag to re-register

def check_system(client, key, systems):
    try:
        #client, key = connect_suma()
        res = client.system.search.hostname(key, systems)
        if res is None:
            print("WARNING ! No such system found with name: " + systems)
        else:
            return res[0].get('id')
    except Exception:
        print("ERROR! system check failed. Can't connect with Uyuni Server.")
    
# Step -4  Run a script for pre patching artifact.
def add_prescript(client, key, sid, chain, prescpt):
    try:
        #client, key = connect_suma()
        res = client.actionchain.addScriptRun(key, sid, chain, '0', '0', 600, prescpt)
        if res is None:
            print("WARNING ! No Pre-patching script added to  chain: " + chain + "for server: " + str(sid))
        else:
            #print("Pre-Patching script added with action ID: " + str(res))
            return res
    except Exception:
        print("ERROR! Pre- Patching script can't be added. Can't connect with Uyuni Server.")
  
# Step- 5, List "listLatestUpgradablePackages" for a system.
def list_pkg(client, key, sysid):
    try:
        #client, key = connect_suma() ## Passing session and key in args
        res = client.system.listLatestUpgradablePackages(key,sysid)
        print("Connected")
        pkg_ids = []
        for val in res:
            pkg_ids.append(val.get('to_package_id'))
        return pkg_ids
    
    except Exception:
        print("ERROR! list_pkg failed. Can't connect with Uyuni Server") 
# Step -6, Schedule package upgrade for a system "schedulePackageInstall". 
def upgrade(client, key, sysid, pkglist, chain_name):
    try:
        res = client.actionchain.addPackageUpgrade(key, sysid, pkglist, chain_name)
        if res is None:
            print("Error ! No upgrade action schedule")
        else:
            #print("Upgrade in Progress with action ID: " + str(res))
            return res
    except Exception:
        print("Error! There is an error in upgrade")
# Step -7, Schedule a script Run for post patching artifact but before server reboot.
def add_postscript(client, key, sid, chain, postscpt):
    sid = int(sid)
    try:
        res = client.actionchain.addScriptRun(key, sid, chain, '0', '0', 600, postscpt)
        if res is None:
            print("WARNING ! No Post-reboot-patching script added to  chain: " + chain + "for server: " + str(sid))
        else:
            #print("Post-reboot-patching script added with action ID: " + str(res))
            return res
    except Exception:
        print("ERROR! Post-reboot-patching script can't be added. Can't connect with Uyuni Server.")
        
# Step -8, Schedule a reboot post install.
def add_reboot(client, key, sysid, chain_name):
    try:
        res = client.actionchain.addSystemReboot(key, sysid, chain_name)
        if res is None:
            print("Error ! No reboot action added")
        else:
            #print("Added reboot with action ID: " + str(res))
            return res
    except Exception:
        print("Error! There is an error in add reboot")
# Step -9, Schedule an action chain
def schedule_chain(client, key, chain_name, sch):
    try:
        schedule = iso8601.parse_date(sch)
        res = client.actionchain.scheduleChain(key, chain_name, schedule)
        #print(res)
        if res is None:
            print("Error ! No ChainAction action Scheduled.")
        else:
            return res
            #print("Scheduled Chain action with action ID: " + str(res))
    except Exception:
        print("Error! There is an error in schedule chain.")
# Step -10, Schedule a script Run for post patching artifact & post node reboot.

def cal_slicing(str1):
    val = str1.split(':')
    year = int(val[0])
    month = int(val[1])
    mdate = int(val[2])
    return year, month, mdate    
def time_slicing(str2):
    hh = int(str2.split(':')[0])
    mm = int(str2.split(':')[1])
    return hh, mm
 
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
            upgrade_action = {}
            reboot_action = {}
            for host in systems_name:
                sid = check_system(client, key, host)
                upgradable_list = list_pkg(client, key, sid)
                #print(upgradable_list)
                schedule = datetime(year, month, mdate, hh, mm, tzinfo=timezone.utc).isoformat()
                #print(schedule)
                chain = host + '_PATCH' + (datetime.now().isoformat('T', 'seconds')) # It will create a new chain on every run of script
                #print(chain)
                # base64 encoded bash scripts
                prescpt = " "
                pre_re_scpt = " "
                if not len(upgradable_list):
                    print("MESSAGE: There is NO package applicable to upgrade for Server: " + host)
                else:
                    actionchain(client, key, chain) # Create action chain
                    # Sequence of actions added to action chain
                    pre_aid = add_prescript(client, key, sid, chain, prescpt)   # 1 # Pre patching artifacts script
                    upgrade_aid = upgrade(client, key, sid, upgradable_list, chain) # 2 # Perform packages upgradation.
                    #print("Upgrade action for " + host + " with action ID: %i"% upgrade_aid)
                    pre_re_aid = add_postscript(client, key, sid, chain, pre_re_scpt)  # 3 # Pre-reboot-patching artifacts script
                    reboot_aid = add_reboot(client, key, sid, chain) # 4  # reboot system post upgrade
                    #print("Added reboot for " + host + " with action ID: %i"% reboot_aid)
                    schedule_chain(client, key, chain, schedule) # Schedule action chain for above 4
                    if host not in upgrade_action:
                        upgrade_action[host] = upgrade_aid
                        reboot_action[host] = reboot_aid
                    else:
                        pass
            client.auth.logout(key) ## Logout session with SUSE manager       
            # Create dict for server name and corresponding action IDs
            print("Upgrade action IDs are: \n")
            print(upgrade_action)
            print("\nReboot action IDs are: \n")
            print(reboot_action)                      
        
    except Exception:
        print("ERROR! Custom Python module error. Can't schedule patching with Uyuni Server.")
    
if __name__ == "__main__":
       main()
