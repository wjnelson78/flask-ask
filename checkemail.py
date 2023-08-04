#checkemail.py
import requests
import json
from config import client_id, client_secret, tenant_id, user_id
from database import setup_database, insert_email_if_not_exists, check_new_email

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
    print(f"Received at: {email['receivedDateTime']}\n")


def check_and_update_email_status(access_token, user_id, email_id):
    url = f"https://graph.microsoft.com/v1.0/users/{user_id}/messages/{email_id}"
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # if the request fails, this will raise an exception
    return response.json()['isRead']


def update_email_status_in_database(conn, email_id, is_read):
    c = conn.cursor()
    c.execute('''
        UPDATE emails SET status = ? WHERE id = ?
    ''', ('read' if is_read else 'unread', email_id))
    conn.commit()


if __name__ == "__main__":
    conn = setup_database()
    access_token = get_access_token(client_id, client_secret, tenant_id)

    # check and update the status of emails in the database
    c = conn.cursor()
    c.execute('''
        SELECT id FROM emails WHERE status = 'unread'
    ''')
    unread_emails = c.fetchall()
    for email in unread_emails:
        email_id = email[0]
        is_read = check_and_update_email_status(access_token, user_id, email_id)
        update_email_status_in_database(conn, email_id, is_read)

    latest_emails = get_latest_emails(access_token, user_id)
    for email in latest_emails:
        print_email(email)
        insert_email_if_not_exists(conn, email)

    conn.close()
