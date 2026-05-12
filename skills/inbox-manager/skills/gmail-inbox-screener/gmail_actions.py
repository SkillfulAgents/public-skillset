#!/usr/bin/env python3
"""
Gmail Actions - Mark as read, send replies
"""

import os
import json
import requests
import argparse
import base64
from email.mime.text import MIMEText


def mark_as_read(account_id, email_id, proxy_base, proxy_token):
    """Mark an email as read by removing UNREAD label"""
    headers = {
        "Authorization": f"Bearer {proxy_token}",
        "Content-Type": "application/json"
    }
    url = f"{proxy_base}/{account_id}/gmail.googleapis.com/gmail/v1/users/me/messages/{email_id}/modify"
    data = {"removeLabelIds": ["UNREAD"]}
    response = requests.post(url, headers=headers, json=data)
    return response.status_code == 200


def get_email_details(account_id, email_id, proxy_base, proxy_token):
    """Get email details for replying"""
    headers = {"Authorization": f"Bearer {proxy_token}"}
    url = f"{proxy_base}/{account_id}/gmail.googleapis.com/gmail/v1/users/me/messages/{email_id}"
    response = requests.get(url, headers=headers, params={"format": "metadata", "metadataHeaders": ["From", "Subject", "Message-ID", "References", "In-Reply-To"]})

    if response.status_code != 200:
        return None

    msg_data = response.json()
    headers_list = msg_data.get('payload', {}).get('headers', [])

    result = {
        'thread_id': msg_data.get('threadId'),
        'from': '',
        'subject': '',
        'message_id': '',
        'references': '',
        'in_reply_to': ''
    }

    for header in headers_list:
        name = header.get('name', '').lower()
        value = header.get('value', '')
        if name == 'from':
            result['from'] = value
        elif name == 'subject':
            result['subject'] = value
        elif name == 'message-id':
            result['message_id'] = value
        elif name == 'references':
            result['references'] = value
        elif name == 'in-reply-to':
            result['in_reply_to'] = value

    return result


def send_reply(account_id, email_id, reply_body, proxy_base, proxy_token):
    """Send a reply to an email"""
    # Get original email details
    details = get_email_details(account_id, email_id, proxy_base, proxy_token)
    if not details:
        return False, "Failed to get email details"

    # Extract sender email
    from_header = details['from']
    # Parse email from "Name <email>" format
    if '<' in from_header and '>' in from_header:
        to_email = from_header[from_header.index('<')+1:from_header.index('>')]
    else:
        to_email = from_header

    # Build subject
    subject = details['subject']
    if not subject.lower().startswith('re:'):
        subject = f"Re: {subject}"

    # Build references for threading
    references = details['references']
    if details['message_id']:
        if references:
            references = f"{references} {details['message_id']}"
        else:
            references = details['message_id']

    # Create MIME message
    message = MIMEText(reply_body)
    message['to'] = to_email
    message['subject'] = subject
    if details['message_id']:
        message['In-Reply-To'] = details['message_id']
    if references:
        message['References'] = references

    # Encode message
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

    # Send via Gmail API
    headers = {
        "Authorization": f"Bearer {proxy_token}",
        "Content-Type": "application/json"
    }
    url = f"{proxy_base}/{account_id}/gmail.googleapis.com/gmail/v1/users/me/messages/send"
    data = {
        "raw": raw,
        "threadId": details['thread_id']
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return True, f"Reply sent to {to_email}"
    else:
        return False, f"Failed to send: {response.status_code} - {response.text}"


def main():
    parser = argparse.ArgumentParser(description='Gmail actions')
    parser.add_argument('--action', required=True, choices=['mark-read', 'reply'], help='Action to perform')
    parser.add_argument('--email-id', required=True, help='Gmail message ID')
    parser.add_argument('--account', required=True, help='Gmail account email')
    parser.add_argument('--reply-body', help='Reply body text (for reply action)')
    args = parser.parse_args()

    # Get environment variables
    proxy_base = os.environ.get('PROXY_BASE_URL')
    proxy_token = os.environ.get('PROXY_TOKEN')
    accounts_json = os.environ.get('CONNECTED_ACCOUNTS', '{}')

    if not proxy_base or not proxy_token:
        print(json.dumps({"error": "PROXY_BASE_URL and PROXY_TOKEN must be set"}))
        return

    accounts = json.loads(accounts_json)
    gmail_accounts = accounts.get('gmail', [])

    # Find the account
    account = next((a for a in gmail_accounts if a['name'] == args.account), None)
    if not account:
        print(json.dumps({"error": f"Account {args.account} not found"}))
        return

    account_id = account['id']

    if args.action == 'mark-read':
        success = mark_as_read(account_id, args.email_id, proxy_base, proxy_token)
        print(json.dumps({"success": success, "action": "mark-read", "email_id": args.email_id}))

    elif args.action == 'reply':
        if not args.reply_body:
            print(json.dumps({"error": "Reply body required for reply action"}))
            return
        success, message = send_reply(account_id, args.email_id, args.reply_body, proxy_base, proxy_token)
        print(json.dumps({"success": success, "message": message, "action": "reply", "email_id": args.email_id}))


if __name__ == '__main__':
    main()
