#!/usr/bin/env python3
# Author : pankaj-kumar.goyal@hpe.com
# Purpose: Script will fetch list of out of dated/non-compliant systems from SUSE Manager and will generate a CSV file.
# Usages: python3 <script_name.py> 
# Pre-req: Python3 module "xmlrpclib" should be pre installed.
# Script Name: SUMA_LIST_OUTDATED_SYSTEMS.py

# Step -0, Importing relevent modules

import ssl, csv, os, sys, smtplib
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
# Step -2, Fetch out of date systems list from SUSE manager
def list_out_of_date_systems(client, key):
    try:
        res = client.system.listOutOfDateSystems(key)
        if res is None:
            print("INFO ! No outdated system listed in SUMA.")
        else:
            return res
    except Exception:
        print("ERROR-1! func list_out_of_date_systems().Check SUMA_LIST_COMPLIANT_SYSTEMS.py. Can't Fetch list of out-dated systems.")
def send_email(filetosend):
    sender = 'abcsen@sample.com'
    receiver = 'abc@sample.com'
    msg = MIMEMultipart("alternative")
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = 'SUSE Manager - Outdated Systems List'
    msg['Bcc'] = 'abc@sample.com'
    body = "List Of all outdated systems From Uyuni/SUSE Manager" 
    msg.attach(MIMEText(body, 'plain'))
    attachment = open(filetosend, "rb")
    part = MIMEBase('application', "octet-stream")
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % filetosend)
    msg.attach(part)
    text = msg.as_string()
    try:
        smtpObj = smtplib.SMTP('smtp.abc.com')
        smtpObj.sendmail(sender, receiver, text)
        smtpObj.close()  
        print ("Successfully sent outdated systems list.")
    except Exception:
        print ("Error: Unable to send email. Uffff ")
# Step -4, Main() function starts    
def main():
    try:
        client, key = connect_suma() ## Generate session & session key
        response = list_out_of_date_systems(client, key)
        if os.path.exists("outdated_systems.csv"):   # remove existing out_of_dates_systems.csv file from the system
            os.remove("outdated_systems.csv")
        else:
            pass
        # Create CSV file from fetched data.
        csv_coloumn = response[0].keys()
        with open('outdated_systems.csv', 'w') as output_file:
            dict_writer = csv.DictWriter(output_file, csv_coloumn)
            dict_writer.writeheader()
            dict_writer.writerows(response)
            
        if os.path.exists("outdated_systems.csv"):   # checking if file exist and emailing to user
            send_email("outdated_systems.csv")
        else:
            pass
        client.auth.logout(key) ## Logout session with SUSE manager
    except Exception:
        print("ERROR-2 main() function! Check SUMA_LIST_OUTDATED_SYSTEMS.py. Can't Fetch list of outdated systems.")
    
if __name__ == "__main__":
       main()
