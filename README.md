# Gmail Job Posting Email Reader

A Python script to read all emails from Gmail under the "job_posting" label using the Gmail API.

## Features

- 🔐 Secure authentication with Gmail API
- 📧 Read emails from specific Gmail labels
- 📄 Extract email subjects, senders, dates, and body content
- 💾 Save emails to text files for offline access
- 🔍 Search and filter capabilities
- 📊 Display email summaries and full content

## Prerequisites

- Python 3.7 or higher
- A Gmail account
- Google Cloud Project with Gmail API enabled

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click on it and press "Enable"
   - gamil api is free with certain usage limitation, please refer to [Gmail API Documentation](https://developers.google.com/workspace/gmail/api/reference/quota)

### 3. Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Choose "Desktop application" as the application type
4. Give it a name (e.g., "Gmail Job Posting Reader")
5. Download the credentials file and rename it to `credentials.json`
6. Place `credentials.json` in the same directory as the script
7. It is important to PULISH your app, otherwise you will not be able to access the Gmail API:
    - Go to "OAuth consent screen"
    - Fill in the required fields (App name, User support email, etc.)
    - Save and publish your app
8. The `token.json` file will be created automatically after the first run of the script, which stores your access tokens, so that you don't have to authenticate every time you run the script.
9. You need to delete the `token.json` and then re-run the script if you want to re-authenticate or change the scopes.

### 4. Create Gmail Label

1. Open Gmail in your browser
2. In the left sidebar, click on "Labels" (or the "+" button next to it)
3. Create a new label called "job_posting"
4. Apply this label to the job posting emails you want to read

## Usage

### Basic Usage

```bash
python gmail_reader.py
```

The script will:

1. Authenticate with Gmail API (opens browser for first-time setup)
2. Find the "job_posting" label
3. Retrieve up to 50 emails from that label
4. Display email summaries
5. Ask if you want to save emails to a file
6. Ask if you want to see full email bodies

### Command Line Options

You can also use the script programmatically:

```python
from gmail_reader import GmailJobPostingReader

# Initialize reader
reader = GmailJobPostingReader()

# Authenticate
if reader.authenticate():
    # Get label ID
    label_id = reader.get_label_id('job_posting')

    if label_id:
        # Get emails
        emails = reader.get_emails_from_label(label_id, max_results=100)

        # Print emails
        reader.print_emails(emails, show_body=True)

        # Save to file
        reader.save_emails_to_file(emails, 'my_job_emails.txt')
```

## File Structure

```
job_posting_email_automation/
├── gmail_reader.py          # Main script
├── requirements.txt         # Python dependencies
├── credentials.json         # Gmail API credentials (you need to add this)
├── token.json              # Authentication token (generated automatically)
├── job_posting_emails.txt  # Output file (generated when saving)
└── README.md               # This file
```

## Security Notes

- Never commit `credentials.json` or `token.json` to version control
- The `token.json` file contains your personal access tokens
- Keep your credentials secure and don't share them

## Troubleshooting

### Common Issues

1. **"credentials.json file not found"**

   - Make sure you've downloaded the OAuth 2.0 credentials from Google Cloud Console
   - Rename the downloaded file to `credentials.json`
   - Place it in the same directory as the script

2. **"Label 'job_posting' not found"**

   - Create the label in Gmail first
   - Make sure the label name matches exactly (case-insensitive)
   - The script will show available labels if the requested one isn't found

3. **Authentication errors**

   - Delete `token.json` and try again
   - Make sure your Google Cloud Project has Gmail API enabled
   - Check that your OAuth 2.0 credentials are configured correctly

4. **No emails found**
   - Make sure you have emails with the "job_posting" label
   - Check that the label is applied to the emails you want to read

### API Quotas

- Gmail API has daily quotas (1 billion queries per day for most users)
- The script retrieves emails in batches to avoid hitting rate limits
- If you need to process many emails, consider implementing pagination

## Customization

### Change Label Name

To read emails from a different label, modify the label name in the script:

```python
label_id = reader.get_label_id('your_custom_label_name')
```

### Modify Email Retrieval

You can customize how many emails to retrieve:

```python
emails = reader.get_emails_from_label(label_id, max_results=200)
```

### Add Filters

You can add date filters or other criteria by modifying the `get_emails_from_label` method.

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to submit issues and enhancement requests!


