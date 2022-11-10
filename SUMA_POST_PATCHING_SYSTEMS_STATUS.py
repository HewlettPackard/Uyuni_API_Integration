#!/usr/bin/env python3
# Author : pankaj-kumar.goyal@hpe.com
# Purpose: Script will fetch list of outdated/compliant systems from SUMA. Same will we used to vaidate server patching status 
#           post automated patching. 
# Usages: python3 <script_name.py> <server1,server2,server3> 
# Pre-req: Python3 module "xmlrpclib" should be pre installed.
# Script Name: SUMA_POST_PATCHING_SYSTEMS_STATUS.py

# Importing relevent modules
import ssl, sys, smtplib, csv, os
from xmlrpc.client import ServerProxy
from string import Template
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase 
from email import encoders
# func -1, Setup RPC connection
def connect_suma(mgr_login = '', mgr_pass = ''):
    MANAGER_URL = "https://sample.com/rpc/api"
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
# func -3 Send CSV file over email
def send_email(filetosend):
    sender = 'abc@sample.com'
    receiver = 'abc@sample.com'
    #receiver = 'pankaj-kumar.goyal@hpe.com'
    msg = MIMEMultipart("alternative")
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = 'Post Patching Server status report from Uyuni/SUSE Manager.'
    msg['Bcc'] = 'abc@sample.com'
    body = "Email from NGIT environment for Linux Infrastructure" 
    msg.attach(MIMEText(body, 'plain'))
    attachment = open(filetosend, "rb")
    part = MIMEBase('application', "octet-stream")
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % filetosend)
    msg.attach(part)
    text = msg.as_string()
    try:
        smtpObj = smtplib.SMTP('smtp.sample.com')
        smtpObj.sendmail(sender, receiver, text)
        smtpObj.close()
        print ("Successfully sent post patching servers status to Service-Now for further validation.")
    except Exception:
        print ("Error: Unable to send email to Service-Now")
# func -4, get server details
def check_system(client, key, systems):
    try:
        res = client.system.search.hostname(key, systems)
        if res is None:
            print("WARNING ! No such system found with name: " + systems)
        else:
            return res
    except Exception:
        print("ERROR! system check failed. Can't connect with SUSE manager.")
# func -5, Main() function starts    
def main():
    try:
        # Check if required arguments has been passed at execution of script
        if ( len(sys.argv) != 2 ):
            print("Script need comma seperated list of servers as an argument")
            exit(1)
        else:
            systems_name = sys.argv[1].split(',')  # Create a list of servers passed as an arguments  
        client, key = connect_suma() ## Generate session & session key
        response = list_out_of_date_systems(client, key)
        outdated = [] # Created list of out of dated systems.
        for i in response:
            outdated.append(i['name'].split('.')[0])
        sys_list = []
        for node in systems_name:
            node_detail = check_system(client, key, node)
            if node in outdated:
                non_comp_dict = {'server_id': node_detail[0]['id'], 'server': node_detail[0]['name'], 'patch_compliant': "non-compliant" }
                sys_list.append(non_comp_dict)
            elif len(node_detail):
                comp_dict = {'server_id': node_detail[0]['id'], 'server': node_detail[0]['name'], 'patch_compliant': "compliant" }
                sys_list.append(comp_dict)
            else:
                unknown_dict = {'server_id': "unknown", 'server': node, 'patch_compliant': "non-compliant" }
                sys_list.append(unknown_dict)
        if os.path.exists("postpatch_status.csv"):   # remove existing out_of_dates_systems.csv file from the system
            os.remove("postpatch_status.csv")
        else:
            pass
        # Create CSV file for applicable servers.
        csv_columns = ['server_id', 'server', 'patch_compliant']
        with open('postpatch_status.csv', 'w') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=csv_columns)
            dict_writer.writeheader()
            dict_writer.writerows(sys_list)
        # Email CSV file to Service-NOW
        send_email("postpatch_status.csv")
        
    except Exception:
        print("ERROR-2 main() function! Check SUMA_LIST_COMPLIANT_SYSTEMS.py. Can't systems patching status.")
    
if __name__ == "__main__":
       main()
