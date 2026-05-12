#!/usr/bin/env python3
"""
Gmail Unsubscribe - Extract unsubscribe links from email bodies
"""

import os
import json
import requests
import argparse
import re
import base64
from html.parser import HTMLParser


class UnsubscribeLinkExtractor(HTMLParser):
    """Extract unsubscribe links from HTML content"""

    def __init__(self):
        super().__init__()
        self.links = []
        self.current_href = None
        self.current_text = []
        self.in_link = False

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.in_link = True
            self.current_text = []
            for name, value in attrs:
                if name == 'href' and value:
                    self.current_href = value

    def handle_endtag(self, tag):
        if tag == 'a' and self.in_link:
            text = ''.join(self.current_text).lower()
            href = self.current_href or ''

            # Check if link or text contains unsubscribe
            if 'unsubscribe' in href.lower() or 'unsubscribe' in text:
                if href.startswith('http'):
                    self.links.append(href)
            elif 'opt-out' in href.lower() or 'opt out' in text:
                if href.startswith('http'):
                    self.links.append(href)
            elif 'manage preferences' in text or 'email preferences' in text:
                if href.startswith('http'):
                    self.links.append(href)

            self.in_link = False
            self.current_href = None
            self.current_text = []

    def handle_data(self, data):
        if self.in_link:
            self.current_text.append(data)


def decode_base64url(data):
    """Decode base64url encoded data"""
    # Add padding if needed
    padding = 4 - len(data) % 4
    if padding != 4:
        data += '=' * padding
    # Replace URL-safe characters
    data = data.replace('-', '+').replace('_', '/')
    try:
        return base64.b64decode(data).decode('utf-8', errors='replace')
    except Exception:
        return ''


def get_email_body(msg_data):
    """Extract email body from message data"""
    payload = msg_data.get('payload', {})

    # Check for body directly in payload
    body_data = payload.get('body', {}).get('data', '')
    if body_data:
        return decode_base64url(body_data)

    # Check parts
    parts = payload.get('parts', [])
    html_body = ''
    text_body = ''

    def extract_from_parts(parts):
        nonlocal html_body, text_body
        for part in parts:
            mime_type = part.get('mimeType', '')
            body_data = part.get('body', {}).get('data', '')

            if body_data:
                decoded = decode_base64url(body_data)
                if mime_type == 'text/html':
                    html_body = decoded
                elif mime_type == 'text/plain':
                    text_body = decoded

            # Recurse into nested parts
            nested_parts = part.get('parts', [])
            if nested_parts:
                extract_from_parts(nested_parts)

    extract_from_parts(parts)

    return html_body or text_body


def extract_unsubscribe_links(html_content):
    """Extract unsubscribe links from HTML content"""
    links = []

    # Try HTML parser
    try:
        parser = UnsubscribeLinkExtractor()
        parser.feed(html_content)
        links.extend(parser.links)
    except Exception:
        pass

    # Also try regex for any URLs containing unsubscribe
    url_pattern = r'https?://[^\s<>"\']+unsubscribe[^\s<>"\']*'
    regex_links = re.findall(url_pattern, html_content, re.IGNORECASE)

    # Clean up regex links (remove trailing punctuation)
    for link in regex_links:
        clean_link = re.sub(r'[.,;:!?)]+$', '', link)
        if clean_link not in links:
            links.append(clean_link)

    # Try opt-out links too
    optout_pattern = r'https?://[^\s<>"\']+opt[-_]?out[^\s<>"\']*'
    optout_links = re.findall(optout_pattern, html_content, re.IGNORECASE)
    for link in optout_links:
        clean_link = re.sub(r'[.,;:!?)]+$', '', link)
        if clean_link not in links:
            links.append(clean_link)

    return links


def get_list_unsubscribe_header(headers):
    """Extract List-Unsubscribe header if present"""
    for header in headers:
        if header.get('name', '').lower() == 'list-unsubscribe':
            value = header.get('value', '')
            # Extract HTTP URL from header (may contain mailto: and http:)
            http_match = re.search(r'<(https?://[^>]+)>', value)
            if http_match:
                return http_match.group(1)
    return None


def fetch_email_and_extract_unsubscribe(account_id, account_email, email_id, proxy_base, proxy_token):
    """Fetch email and extract unsubscribe link"""
    headers = {"Authorization": f"Bearer {proxy_token}"}

    # Get full message
    msg_url = f"{proxy_base}/{account_id}/gmail.googleapis.com/gmail/v1/users/me/messages/{email_id}"
    response = requests.get(msg_url, headers=headers, params={"format": "full"})

    if response.status_code != 200:
        return {"error": f"Failed to fetch email: {response.status_code}"}

    msg_data = response.json()

    # Extract metadata
    payload_headers = msg_data.get('payload', {}).get('headers', [])
    subject = ''
    sender = ''

    for header in payload_headers:
        name = header.get('name', '').lower()
        if name == 'subject':
            subject = header.get('value', '')
        elif name == 'from':
            sender = header.get('value', '')

    # Check List-Unsubscribe header first
    list_unsub = get_list_unsubscribe_header(payload_headers)

    # Get email body
    body = get_email_body(msg_data)

    # Extract unsubscribe links from body
    body_links = extract_unsubscribe_links(body)

    # Prioritize links
    unsubscribe_url = None

    if list_unsub:
        unsubscribe_url = list_unsub
    elif body_links:
        # Prefer links with "unsubscribe" in them
        for link in body_links:
            if 'unsubscribe' in link.lower():
                unsubscribe_url = link
                break
        if not unsubscribe_url:
            unsubscribe_url = body_links[0]

    return {
        "email_id": email_id,
        "account": account_email,
        "subject": subject,
        "from": sender,
        "unsubscribe_url": unsubscribe_url,
        "all_unsubscribe_links": body_links,
        "list_unsubscribe_header": list_unsub
    }


def main():
    parser = argparse.ArgumentParser(description='Extract unsubscribe link from email')
    parser.add_argument('--email-id', required=True, help='Gmail message ID')
    parser.add_argument('--account', required=True, help='Gmail account email')
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

    result = fetch_email_and_extract_unsubscribe(
        account['id'],
        account['name'],
        args.email_id,
        proxy_base,
        proxy_token
    )

    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
