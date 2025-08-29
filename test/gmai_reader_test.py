# main.py
import sys
import os

# Add parent directory to sys.path so Python can find gmail_reader.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from gmail_reader import GmailReader

reader = GmailReader('../credentials.json')
messages = reader.get_messages(label_name='job-posting', max_results=5)

for m in messages:
    msg_details = reader.read_message(m['id'])
    print(f"From: {msg_details['from']}")
    print(f"Subject: {msg_details['subject']}")
    print(f"Body preview: {msg_details['body'][:100]}...\n")
