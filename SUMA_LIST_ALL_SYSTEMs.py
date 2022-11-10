#!/usr/bin/env python3
# Author : pankaj-kumar.goyal@hpe.com
# Purpose: Returns a list of systems available in SUSE manager.
# Usages:  python3 <script name.py>
# Pre-req: Python3 module "xmlrpclib" should be pre installed
# Script Name: SUMA_LIST_ALL_SYSTEMS.py
from xmlrpc.client import ServerProxy
import ssl, sys, os, csv, smtplib
from string import Template
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase 
from email import encoders
# Function to connect with SUMA/Uyuni
def connect_suma(mgr_login = '', mgr_pass = ''):
    MANAGER_URL = "https://sample.com/rpc/api"
    MANAGER_LOGIN = mgr_login
    MANAGER_PASSWORD = mgr_pass
    # server SSL configuartion and your local SSL configuration
    context = ssl.create_default_context()
    client = ServerProxy(MANAGER_URL, context=context)
    key = client.auth.login(MANAGER_LOGIN, MANAGER_PASSWORD)
    return client, key
# Function to list all servers
def list_systems(client, key):
    try:
        res = client.system.listSystems(key)
        if res is None:
            print("INFO ! No system available")
        else:
            return res
    except Exception:
        print("ERROR! Can't connect with SUSE manager.")
#Send CSV file over email
def send_email(filetosend):
    sender = 'abcxz@sample.com'
    receiver = 'abc@sample.com'
    msg = MIMEMultipart("alternative")
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = 'List Of All Servers In Uyuni/SUSE Manager'
    msg['Bcc'] = 'abc@sample.com'
    body = "List Of ALL SERVERS From Uyuni/SUSE Manager" 
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
        print ("Successfully sent report over email ! ENJOY.")
    except Exception:
        print ("Error: Unable to send email. Sorry ")   

def main():
    try:
        client, key = connect_suma() ## Generating session & session key
        print("\nListing All Systems............")
        response = list_systems(client, key)
#        print(response[0])
        # Checking and removing if old file exist
        if os.path.exists("suma_all_system_list.csv"):
            os.remove("suma_all_system_list.csv")
        else:
            pass
        # Create CSV file from fetched data.
        csv_coloumn = response[0].keys()
        with open('suma_all_system_list.csv', 'w') as output_file:
            dict_writer = csv.DictWriter(output_file, csv_coloumn)
            dict_writer.writeheader()
            dict_writer.writerows(response)
        if os.path.exists("suma_all_system_list.csv"):
            send_email("suma_all_system_list.csv")
        else:
            print("\nNo file available to send over email ! Thanks")
        client.auth.logout(key) ## Logout session with SUSE manager
    except Exception:
        print("ERROR! Check script SUMA_LIST_ALL_SYSTEMS . Can't Fetch list of Systems.")
    
if __name__ == "__main__":
       main()