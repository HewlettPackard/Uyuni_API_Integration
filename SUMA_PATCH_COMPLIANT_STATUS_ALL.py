#!/usr/bin/env python3
# Author : pankaj-kumar.goyal@hpe.com
# Purpose: Script will fetch list of non-compliant/compliant systems from SUMA. Same will be send across over email. 
# Usages: python3 <script_name.py> 
# Pre-req: Python3 module "xmlrpclib" should be pre installed.
# Script Name: SUMA_PATCH_COMPLIANT_STATUS_ALL.py

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
            print("INFO ! No system listed in SUMA.")
        else:
            return res
    except Exception:
        print("ERROR-1! func list_out_of_date_systems().Check SUMA_PATCH_COMPLIANT_STATUS_ALL.py. Can't Fetch list of systems.")
# func -3 Send CSV file over email
def send_email(filetosend):
    sender = 'abcsen@sample.com'
    receiver = 'abcrec@sample.com'
    msg = MIMEMultipart("alternative")
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = 'Uyuni/SUSE Manager - Patch compliance List for All Servers.'
    msg['Bcc'] = 'abc@sample.com'
    body = "Uyuni/SUSE Manager - Patch compliance List for All Servers" 
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
        print ("Successfully sent systems list from SUMA. WOW!")
    except Exception:
        print ("Error: Unable to send email. SORRY")
# func -4, list all systems available in SUMA
def list_systems(client, key):
    try:
        res = client.system.listSystems(key)
        #print (res)
        if res is None:
            print("INFO ! No system available")
        else:
            return res
    except Exception:
        print("ERROR! Can't connect with SUSE manager.")
# func -5, Main() function starts    
def main():
    try:
        
        client, key = connect_suma() ## Generate session & session key
        response1 = list_systems(client, key)
        response2 = list_out_of_date_systems(client, key)
        outdated = [] # Created list of out of dated systems.
        sys_list = []   # to save non-compliant/compliant systems data
        ENV = "NGIT" ## Set Data-Center Environment NGIT or PVC1 or PVC2
        
        for i in response2:
            dict2 = {'server_id': i['id'], 'server': i['name'], 'env': ENV, 'last_checkin': i['last_checkin'], 'patch_compliant': "non-compliant", 'outdated_pkg_count': i['outdated_pkg_count']}
            outdated.append(i['name'])
            sys_list.append(dict2)
        for i in response1:
            if i['name'] in outdated:
                pass
            else:
                dict1 = {'server_id': i['id'], 'server': i['name'], 'env': ENV, 'last_checkin': i['last_checkin'], 'patch_compliant': "compliant", 'outdated_pkg_count': "0"}
                sys_list.append(dict1)
        if os.path.exists("All_PATCH_COMPLIANCE_STATUS.csv"):   # remove existing csv file from the system
            os.remove("All_PATCH_COMPLIANCE_STATUS.csv")
        else:
            pass
        # Create CSV file for applicable servers.
        csv_columns = ['server_id', 'server', 'env', 'last_checkin', 'patch_compliant', 'outdated_pkg_count']
        with open('All_PATCH_COMPLIANCE_STATUS.csv', 'w') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=csv_columns)
            dict_writer.writeheader()
            dict_writer.writerows(sys_list)
        # Email CSV file
        if os.path.exists("All_PATCH_COMPLIANCE_STATUS.csv"):
            send_email("All_PATCH_COMPLIANCE_STATUS.csv")
        else:
            print("\nNo file available to send over email ! Thanks")
        client.auth.logout(key) ## Logout session with SUSE manager
        
    except Exception:
        print("ERROR-2 main() function! Check SUMA_PATCH_COMPLIANT_STATUS_ALL.py. Can't fetch status report.")
    
if __name__ == "__main__":
       main()
    