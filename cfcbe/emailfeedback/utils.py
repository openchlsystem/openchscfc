import imaplib
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime
from .models import Email


def fetch_emails(email_address, email_password, imap_host = 'mail.bitz-itc.com'):
    try:
        # Connect to the IMAP server
        server = imaplib.IMAP4_SSL(imap_host)
        server.login(email_address, email_password)
        server.select('inbox')

        # Search for all emails
        # Search for unread emails only
        status, messages = server.search(None, 'UNSEEN')
        email_ids = messages[0].split()

        for e_id in email_ids:
            # Fetch the email
            status, msg_data = server.fetch(e_id, '(RFC822)')
            if status != 'OK':
                continue  # Skip if fetching fails

            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            # Decode email headers
            subject, encoding = decode_header(msg['Subject'])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or 'utf-8')

            sender, encoding = decode_header(msg['From'])[0]
            if isinstance(sender, bytes):
                sender = sender.decode(encoding or 'utf-8')

            recipient = email_address  # Emails fetched are for this account

            # Extract the email date
            date_header = msg['Date']
            received_date = None
            if date_header:
                try:
                    received_date = parsedate_to_datetime(date_header)
                except Exception as e:
                    print(f"Error parsing email date: {e}")
                    continue  # Skip this email if the date is invalid

            # Extract email body
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    # Check for text/plain parts
                    if part.get_content_type() == "text/plain" and part.get_content_disposition() is None:
                        body = part.get_payload(decode=True).decode()
                        break
            else:
                # Handle non-multipart emails
                body = msg.get_payload(decode=True).decode()

            # Save to the database if it doesn't already exist
            if not Email.objects.filter(
                sender=sender,
                recipient=recipient,
                subject=subject,
                body=body,
                received_date=received_date
            ).exists():
                Email.objects.create(
                    sender=sender,
                    recipient=recipient,
                    subject=subject,
                    body=body,
                    received_date=received_date,
                )

        # Close the server connection
        server.close()
        server.logout()

    except Exception as e:
        print(f"An error occurred: {e}")
