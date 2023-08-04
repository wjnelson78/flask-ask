#################################################################################
# Check Office 365 for new email                                                #
# Built by William Nelson                                                       #
# Built 2021                                                                    #
# williamjnelson@me.com                                                         #
#                                                                               #
#                                                                               #
#################################################################################
#                                                                               #
# To access Microsoft Graph API, you will need to create an app registration in #
# the Azure portal, which will provide you with a tenant ID, client ID, and     #
# client secret. Then, use these to obtain an access token which can be used to #
# authenticate your requests.                                                   #
#                                                                               #
# Replace 'YOUR_CLIENT_ID', 'YOUR_CLIENT_SECRET', 'YOUR_TENANT_ID' and          #
# 'USER_ID_OR_EMAIL_ADDRESS' with your actual values. Make sure to keep these   #
# credentials safe and secure, and do not expose them publicly.                 #
#                                                                               #
#                                                                               #
#################################################################################

import requests
import json
from config import client_id, client_secret, tenant_id, user_id


def get_access_token(client_id, client_secret, tenant_id):
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://graph.microsoft.com/.default'
    }
    response = requests.post(url, data=payload)
    response.raise_for_status()  # if the request fails, this will raise an exception
    return response.json()['access_token']


def get_latest_emails(access_token, user_id):
    url = f"https://graph.microsoft.com/v1.0/users/{user_id}/mailFolders/Inbox/messages?$filter=isRead eq false"
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # if the request fails, this will raise an exception
    return response.json()['value']

def print_email(email):
    print(f"Subject: {email['subject']}")
    print(f"From: {email['from']['emailAddress']['name']} <{email['from']['emailAddress']['address']}>")
    print(f"Received at: {email['receivedDateTime']}")
    print(f"Preview: {email['bodyPreview']}\n")
    
if __name__ == "__main__":
    access_token = get_access_token(client_id, client_secret, tenant_id)
    latest_emails = get_latest_emails(access_token, user_id)
    for email in latest_emails:
        print_email(email)
