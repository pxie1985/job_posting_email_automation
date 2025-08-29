# gmail_reader_module.py

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import base64
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import message_from_bytes
import re

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.modify'
]
TOKEN_FILE = 'token.json'


class GmailReader:
    def __init__(self, credentials_file='credentials.json'):
        self.credentials_file = credentials_file
        self.service = self.authenticate()

    def authenticate(self):
        """Authenticate and create the Gmail service, using saved token if available."""
        creds = None
        if os.path.exists(TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)

            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())

        return build('gmail', 'v1', credentials=creds)

    def get_label_id(self, label_name):
        """Get Gmail label ID by name"""
        labels_result = self.service.users().labels().list(userId='me').execute()
        labels = labels_result.get('labels', [])
        for label in labels:
            if label['name'] == label_name:
                return label['id']
        return None

    def get_messages(self, label_name='job-posting', max_results=10):
        """List messages under a specific label"""
        label_id = self.get_label_id(label_name)
        if not label_id:
            print(f"Label '{label_name}' not found.")
            return []

        messages_result = self.service.users().messages().list(
            userId='me',
            labelIds=[label_id],
            maxResults=max_results
        ).execute()

        return messages_result.get('messages', [])

    def _add_footer(self, msg, footer_text):
        """Recursively adds a footer to the text/plain or text/html parts of a message."""
        if msg.is_multipart():
            for part in msg.get_payload():
                self._add_footer(part, footer_text)
        elif msg.get_content_type() in ['text/plain', 'text/html']:
            original_payload = msg.get_payload(decode=True)
            if original_payload:
                charset = msg.get_content_charset() or 'utf-8'
                decoded_text = original_payload.decode(charset, errors='ignore')
                modified_text = f"{decoded_text}\n\n{footer_text}"
                msg.set_payload(modified_text, charset)
        return msg


    # In the GmailReader class
    # In the GmailReader class
    def create_draft_from_email(self, msg_id):
        """
        Reads a single message by ID, adds a footer, and creates a new draft.
        This draft will be formatted to look like a forwarded email.
        """
        try:
            # 1. Get the full raw message data
            msg_data = self.service.users().messages().get(
                userId='me', id=msg_id, format='raw'
            ).execute()
            raw_message_bytes = base64.urlsafe_b64decode(msg_data['raw'])

            # 2. Parse the raw bytes into a MIME message object
            original_mime_message = message_from_bytes(raw_message_bytes)

            # 3. Create a new multipart message for the draft
            new_mime_message = MIMEMultipart('mixed')

            # 4. Set headers to simulate a forwarded email
            new_mime_message['To'] = ""  # Keep the "To" field blank for a draft
            new_mime_message['From'] = self.service.users().getProfile(userId='me').execute()['emailAddress']

            # Add the "Fwd:" prefix to the original subject
            original_subject = original_mime_message.get("Subject", "")
            new_mime_message['Subject'] = f"Fwd: {original_subject}"

            # Define the new footer content
            # Define the new footer content
            footer_plain = (
                "Archive of job postings (https://ladners.org/jobpostings/) | "
                "About page with unsubscribe information (https://ladners.org/jobpostings/about/)"
            )

            # Make Archive of job postings a hyperlink in HTML
            footer_html = (
                '<a href="https://ladners.org/jobpostings/" target="_blank">Archive of job postings</a> | '
                '<a href="https://ladners.org/jobpostings/about/" target="_blank">About page with unsubscribe information</a>'
            )

            # 5. Create the new body with the original message and a footer
            full_body_content = ""
            # Look for the best body content (prefer HTML)
            if self._get_mime_part(original_mime_message, 'text/html'):
                original_html = self._get_mime_part(original_mime_message, 'text/html').get_payload(decode=True).decode(
                    'utf-8', errors='ignore')
                # Create a blockquote-like HTML structure for the forwarded content
                full_body_content = f"<div><br>---------- Forwarded message ---------<br>From: {original_mime_message.get('From')}<br>Date: {original_mime_message.get('Date')}<br>Subject: {original_mime_message.get('Subject')}<br>To: {original_mime_message.get('To')}<br><br>{original_html}</div>"
                full_body_content += f"<div><br><br><hr><i>{footer_html}</i></div>"
            else:  # Fall back to plain text
                original_plain = self._get_mime_part(original_mime_message, 'text/plain').get_payload(
                    decode=True).decode('utf-8', errors='ignore')
                # Create a text-based forwarded header
                full_body_content = f"---------- Forwarded message ---------\nFrom: {original_mime_message.get('From')}\nDate: {original_mime_message.get('Date')}\nSubject: {original_mime_message.get('Subject')}\nTo: {original_mime_message.get('To')}\n\n{original_plain}"
                full_body_content += f"<div><br><br><hr><i>{footer_html}</i></div>"

            # 6. Attach the new body to the message
            if self._get_mime_part(original_mime_message, 'text/html'):
                new_mime_message.attach(MIMEText(full_body_content, 'html', 'utf-8'))
            else:
                new_mime_message.attach(MIMEText(full_body_content, 'plain', 'utf-8'))

            # 7. Handle attachments
            for part in original_mime_message.walk():
                if part.get_filename():
                    new_mime_message.attach(part)

            # 8. Create the draft with the updated message
            encoded_message = base64.urlsafe_b64encode(new_mime_message.as_bytes()).decode()
            draft = {
                'message': {
                    'raw': encoded_message
                }
            }
            created_draft = self.service.users().drafts().create(userId='me', body=draft).execute()
            print(f"Draft created successfully with ID: {created_draft['id']}")
            return created_draft
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def _get_mime_part(self, msg, content_type):
        """Helper function to recursively find a MIME part by content type."""
        if msg.is_multipart():
            for part in msg.get_payload():
                result = self._get_mime_part(part, content_type)
                if result:
                    return result
        elif msg.get_content_type() == content_type:
            return msg
        return None

    def move_message_to_processed(self, msg_id, src_label='job_posting', dest_label='job_posting_processed'):
        """Move a message from src_label to dest_label."""
        try:
            src_label_id = self.get_label_id(src_label)
            dest_label_id = self.get_label_id(dest_label)

            if not dest_label_id:
                # If destination label doesn't exist, create it
                label_body = {
                    'name': dest_label,
                    'labelListVisibility': 'labelShow',
                    'messageListVisibility': 'show'
                }
                created_label = self.service.users().labels().create(userId='me', body=label_body).execute()
                dest_label_id = created_label['id']

            # Modify the message: add dest_label, remove src_label
            body = {
                'addLabelIds': [dest_label_id],
                'removeLabelIds': [src_label_id] if src_label_id else []
            }
            self.service.users().messages().modify(
                userId='me',
                id=msg_id,
                body=body
            ).execute()

            print(f"Message {msg_id} moved from '{src_label}' to '{dest_label}'")
        except Exception as e:
            print(f"Error moving message {msg_id}: {e}")





if __name__ == "__main__":
    reader = GmailReader('credentials.json')
    # Use a label that you know has emails in it, or use 'INBOX'
    messages = reader.get_messages(label_name='job_posting', max_results=20)

    if messages:
        first_message_id = messages[0]['id']
        print(f"Processing message with ID: {first_message_id}")
        draft = reader.create_draft_from_email(first_message_id)
        if draft:
            reader.move_message_to_processed(first_message_id, src_label='job_posting', dest_label='job_posting_processed_xp')
    else:
        print("No messages found under the specified label.")