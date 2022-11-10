#!/usr/bin/env python3
# Author : pankaj-kumar.goyal@hpe.com
# Purpose: To push a server patching schedule on SUSE manager. Script will accept "list of server" & "schedule" as
#          an arguments with script. 
# Usages: This script will accept three arguments in format: <server1,server2,server3> <YYYY:MM:DD> <HH:MM>
#         so here the sample to run: 
#           <script_name.py> <server1,server2,server3> <YYYY:MM:DD> <HH:MM>
# Pre-req: Script should be run with "root". Python3 module "iso8601" & "xmlrpclib" should be pre installed.
# Script Name: uyuni_sction_schedular.py
# created on 24-Jun-2022

# Import respective modules & fucntions
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
# Step- 2, Create an action chain
def actionchain(client, key, chain_name):
    res = client.actionchain.createChain(key,chain_name)
    return res

# Step- 3, input list of servers to be patched and check if its registered on SUMA. If not registered, raise flag to bootstrap

def check_system(client, key, systems):
    try:
        #client, key = connect_suma()
        res = client.system.search.hostname(key, systems)
        if res is None:
            print("WARNING ! No such system found with name: {} ".format(systems))
        else:
            return res[0].get('id')
    except Exception:
        print("ERROR! system check failed. check_system function.")
    
# Step -4  Add do_patch.sh script with action chain.
def add_script(client, key, sid, chain, do_script):
    try:
        #client, key = connect_suma()
        res = client.actionchain.addScriptRun(key, sid, chain, '0', '0', 600, do_script)
        if res is None:
            print("NOTIFICATION ! No do_patch script added to chain: " + chain + "for server: " + str(sid))
        else:
            #print("Pre-Patching script added with action ID: " + str(res))
            return res
    except Exception:
        print("ERROR! Check add_script function.")
# Step- 5, Schedule an action chain  
def schedule_chain(client, key, chain_name, sch):
    try:
        schedule = iso8601.parse_date(sch)
        res = client.actionchain.scheduleChain(key, chain_name, schedule)
        #print(res)
        if res is None:
            print("ERROR ! Can't schedule Chain Action. schedule_chain function")
        else:
            return res
    except Exception:
        print("Error! There is an error in schedule_chain function.")

# Step -6 date and time calculation 
def cal_slicing(str1):
    val = str1.split(':')
    year = int(val[0])
    month = int(val[1])
    mdate = int(val[2])
    return year, month, mdate 
# Step -7 date and time calculation    
def time_slicing(str2):
    hh = int(str2.split(':')[0])
    mm = int(str2.split(':')[1])
    return hh, mm
# Step -8 Main function call 
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
            for host in systems_name:
                sid = check_system(client, key, host)
                rnum = int(random.randint(1, 15))
                if (rnum <10):
                    mmin = "%02d" % rnum
                    schedule = datetime(year, month, mdate, hh, mmin, tzinfo=timezone.utc).isoformat()
                else:
                    mmin = rnum
                    schedule = datetime(year, month, mdate, hh, mmin, tzinfo=timezone.utc).isoformat()
                
                chain = host + '_PATCH' + (datetime.now().isoformat('T', 'seconds')) # It will create a new chain on every run of script
                # base64 encoded bash scripts
                do_script = ""
                actionchain(client, key, chain) # Create action chain
                add_script(client, key, sid, chain, do_script)   # 1 # Pre patching artifacts script
                schedule_chain(client, key, chain, schedule) # Schedule action chain for above 4
                print("DO_Script Run action was created SUCCESSFULLY for: {}".format(host))
            client.auth.logout(key) ## Logout session with SUSE manager       
        
    except Exception:
        print("ERROR! there is an error exception in main() function.")
    
if __name__ == "__main__":
       main()
