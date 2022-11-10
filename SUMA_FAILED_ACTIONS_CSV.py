#!/usr/bin/env python3
# Author : pankaj-kumar.goyal@hpe.com
# Purpose: List all failed actions
# Usages:  python3 <script name.py>
# Pre-req: Python3 module "xmlrpclib" should be pre installed.
# Script Name: SUMA_FAILED_ACTIONS_CSV.py
from xmlrpc.client import ServerProxy
from string import Template
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase 
from email import encoders
import ssl, sys, smtplib, csv, os
# Create Connection
def connect_suma(mgr_login = '', mgr_pass = ''):
    MANAGER_URL = "https://sample.com/rpc/api"
    MANAGER_LOGIN = mgr_login
    MANAGER_PASSWORD = mgr_pass
    # server SSL configuartion and your local SSL configuration
    context = ssl.create_default_context()
    client = ServerProxy(MANAGER_URL, context=context)
    key = client.auth.login(MANAGER_LOGIN, MANAGER_PASSWORD)
    return client, key
#list failed actions
def list_failed_actions(client, key):
    try:
        res = client.schedule.listFailedActions(key)
        if res is None:
            print("INFO ! No action is listed in SUMA.")
        else:
            return res
            #return res[0].get('id')
    except Exception:
        print("ERROR! Action listing fail. Can't connect with SUSE manager.")  
#Send CSV file over email
def send_email(filetosend):
    sender = 'sender@sample.com'
    receiver = 'reveiver@sample.com'
    #receiver = 'pankaj-kumar.goyal@hpe.com'
    msg = MIMEMultipart("alternative")
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = 'SUSE Manager - Failed Actions List'
    msg['Bcc'] = 'receiver@sample.com'
    body = "List Of Failed Actions From Uyuni/SUSE Manager" 
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
        print ("Successfully sent failed actions list.")
    except Exception:
        print ("Error: Unable to send email. Uffff ")

def main():
    try:
        client, key = connect_suma() ## Generating session & session key
        response = list_failed_actions(client, key)
        data_list = [] # List of dictionary
        
        # Create list of dictonories with failed actions data.
        if not len(response):
            print("There is no action marked as FAILED.")
        else:
           for val in response:
               failed_act_dict = {'action_id': val['id'], 'name': val['name'], 'DateTime': val['earliest'], 'CompletedSystems': val['completedSystems'], 'FailedSystems': val['failedSystems'], 'InProgressSystems': val['inProgressSystems'] }
               data_list.append(failed_act_dict)
        ## remove existing suma_failed_actions.csv file from the system if exist
        if os.path.exists("suma_failed_actions.csv"):   
            os.remove("suma_failed_actions.csv")
        else:
            pass
        # Creating CSV file
        csv_columns = ['action_id', 'name', 'DateTime', 'CompletedSystems', 'FailedSystems', 'InProgressSystems']
        with open('suma_failed_actions.csv', 'w') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=csv_columns)
            dict_writer.writeheader()
            dict_writer.writerows(data_list)
        # Email CSV file to an email ID
        if os.path.exists("suma_failed_actions.csv"):   
            send_email("suma_failed_actions.csv")
        else:
            pass
        client.auth.logout(key) ## Logout session with SUSE manager
    except Exception:
        print("ERROR! Check SUMA_FAILED_ACTIONS_CSV . Can't Fetch list of Failed actions.")
    
if __name__ == "__main__":
       main()
    
