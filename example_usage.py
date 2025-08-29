
from gmail_reader import GmailReader



reader = GmailReader('credentials.json')
# Use a label that you know has emails in it. In my case, I created a label called 'job_posting'
messages = reader.get_messages(label_name='job_posting', max_results=10)

if messages:
    for message in messages:
        message_id = message['id']
        print(f"Processing message with ID: {message_id}")
        draft = reader.create_draft_from_email(message_id)
        if draft:
            reader.move_message_to_processed(message_id, src_label='job_posting',
                                             dest_label='job_posting_processed_xp')
else:
    print("No messages found under the specified label.")
