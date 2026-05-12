#!/usr/bin/env python3
"""
Gmail Inbox Screener - Fetch, categorize, and manage recent emails
"""

import os
import json
import requests
import argparse
from datetime import datetime, timezone, timedelta
from urllib.parse import quote
import base64
import re

# Marketing/unimportant indicators
MARKETING_SENDERS = [
    'noreply', 'no-reply', 'newsletter', 'marketing', 'promo', 'deals',
    'notifications', 'updates@', 'info@', 'hello@', 'team@', 'support@',
    'news@', 'digest@', 'weekly@', 'daily@', 'alert@', 'mailer-daemon',
    'postmaster', 'donotreply', 'automated', 'notification@'
]

MARKETING_SUBJECTS = [
    'unsubscribe', 'newsletter', 'weekly digest', 'daily digest', 'promotion',
    'sale', 'discount', 'off your', '% off', 'deal', 'offer', 'limited time',
    'don\'t miss', 'last chance', 'act now', 'free shipping', 'order confirmation',
    'your receipt', 'payment received', 'subscription', 'renewal', 'verify your',
    'confirm your', 'welcome to', 'getting started', 'new features', 'product update',
    'what\'s new', 'roundup', 'highlights', 'trending', 'recommended for you'
]

MARKETING_LABELS = [
    'CATEGORY_PROMOTIONS', 'CATEGORY_UPDATES', 'CATEGORY_SOCIAL',
    'CATEGORY_FORUMS', 'SPAM'
]

IMPORTANT_LABELS = [
    'IMPORTANT', 'STARRED', 'CATEGORY_PERSONAL'
]


def is_marketing_email(email_data):
    """Determine if an email is marketing/unimportant"""
    sender = email_data.get('from', '').lower()
    subject = email_data.get('subject', '').lower()
    labels = email_data.get('labels', [])

    # Check if it has important labels
    for label in IMPORTANT_LABELS:
        if label in labels:
            return False

    # Check if it has marketing labels
    for label in MARKETING_LABELS:
        if label in labels:
            return True

    # Check sender patterns
    for pattern in MARKETING_SENDERS:
        if pattern in sender:
            return True

    # Check subject patterns
    for pattern in MARKETING_SUBJECTS:
        if pattern in subject:
            return True

    return False


def get_email_link(email_id, account_email):
    """Generate a Gmail web link for an email"""
    # Gmail web URL format
    return f"https://mail.google.com/mail/u/{account_email}/#inbox/{email_id}"


def fetch_emails(account_id, account_email, hours, proxy_base, proxy_token):
    """Fetch emails from the last N hours"""
    # Calculate the timestamp for N hours ago
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    since_timestamp = int(since.timestamp())

    # Gmail API query for recent emails
    query = f"after:{since_timestamp}"

    headers = {"Authorization": f"Bearer {proxy_token}"}

    # List messages
    list_url = f"{proxy_base}/{account_id}/gmail.googleapis.com/gmail/v1/users/me/messages"
    params = {"q": query, "maxResults": 100}

    response = requests.get(list_url, headers=headers, params=params)

    if response.status_code != 200:
        print(f"Error fetching messages for {account_email}: {response.status_code}")
        print(response.text)
        return []

    data = response.json()
    messages = data.get('messages', [])

    emails = []
    for msg in messages:
        msg_id = msg['id']
        # Get full message details
        msg_url = f"{proxy_base}/{account_id}/gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}"
        msg_response = requests.get(msg_url, headers=headers, params={"format": "metadata", "metadataHeaders": ["From", "Subject", "Date"]})

        if msg_response.status_code != 200:
            continue

        msg_data = msg_response.json()

        # Extract headers
        headers_list = msg_data.get('payload', {}).get('headers', [])
        email_info = {
            'id': msg_id,
            'thread_id': msg_data.get('threadId'),
            'labels': msg_data.get('labelIds', []),
            'snippet': msg_data.get('snippet', ''),
            'from': '',
            'subject': '',
            'date': '',
            'account': account_email,
            'link': get_email_link(msg_id, account_email),
            'is_unread': 'UNREAD' in msg_data.get('labelIds', [])
        }

        for header in headers_list:
            name = header.get('name', '').lower()
            value = header.get('value', '')
            if name == 'from':
                email_info['from'] = value
            elif name == 'subject':
                email_info['subject'] = value
            elif name == 'date':
                email_info['date'] = value

        email_info['is_marketing'] = is_marketing_email(email_info)
        emails.append(email_info)

    return emails


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


def main():
    parser = argparse.ArgumentParser(description='Screen Gmail inboxes')
    parser.add_argument('--hours', type=int, default=12, help='Hours to look back')
    parser.add_argument('--mark-read', action='store_true', help='Mark marketing emails as read')
    args = parser.parse_args()

    # Get environment variables
    proxy_base = os.environ.get('PROXY_BASE_URL')
    proxy_token = os.environ.get('PROXY_TOKEN')
    accounts_json = os.environ.get('CONNECTED_ACCOUNTS', '{}')

    if not proxy_base or not proxy_token:
        print("Error: PROXY_BASE_URL and PROXY_TOKEN must be set")
        return

    accounts = json.loads(accounts_json)
    gmail_accounts = accounts.get('gmail', [])

    if not gmail_accounts:
        print("Error: No Gmail accounts connected")
        return

    all_emails = []

    for account in gmail_accounts:
        account_id = account['id']
        account_email = account['name']
        print(f"Fetching emails from {account_email}...", file=__import__('sys').stderr)

        emails = fetch_emails(account_id, account_email, args.hours, proxy_base, proxy_token)
        all_emails.extend(emails)

    # Separate marketing and important emails
    marketing_emails = [e for e in all_emails if e['is_marketing'] and e['is_unread']]
    important_emails = [e for e in all_emails if not e['is_marketing'] and e['is_unread']]

    # Mark marketing emails as read if requested
    marked_count = 0
    if args.mark_read:
        for email in marketing_emails:
            account = next((a for a in gmail_accounts if a['name'] == email['account']), None)
            if account:
                if mark_as_read(account['id'], email['id'], proxy_base, proxy_token):
                    marked_count += 1

    # Output results as JSON
    result = {
        'marketing_emails': marketing_emails,
        'important_emails': important_emails,
        'marked_as_read_count': marked_count,
        'total_unread_marketing': len(marketing_emails),
        'total_unread_important': len(important_emails)
    }

    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
