import imaplib
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime
from .models import Email
import requests
import logging
import json
import base64


def fetch_emails(email_address, email_password, imap_host="mail.bitz-itc.com"):
    try:
        # Connect to the IMAP server
        server = imaplib.IMAP4_SSL(imap_host)
        server.login(email_address, email_password)
        server.select("inbox")

        # Search for all emails
        # Search for unread emails only
        status, messages = server.search(None, "ALL")
        email_ids = messages[0].split()

        for e_id in email_ids:
            # Fetch the email
            status, msg_data = server.fetch(e_id, "(RFC822)")
            if status != "OK":
                continue  # Skip if fetching fails

            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            # Decode email headers
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or "utf-8")

            sender, encoding = decode_header(msg["From"])[0]
            if isinstance(sender, bytes):
                sender = sender.decode(encoding or "utf-8")

            recipient = email_address  # Emails fetched are for this account

            # Extract the email date
            date_header = msg["Date"]
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
                    if (
                        part.get_content_type() == "text/plain"
                        and part.get_content_disposition() is None
                    ):
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
                received_date=received_date,
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


def forward_email_to_main_system(email):
    """
    Sends the email details to the main system via a POST request.

    :param email: Email object to be forwarded
    """
    # Define the API endpoint and authentication details
    api_url = "https://demo-openchs.bitz-itc.com/helpline/api/msg/"  # Replace with the actual URL
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer sccjqsonvfvro3v2pn80iat2me",
    }
    # Construct the payload
    payload = {
        "sender": email.sender,
        "recipient": email.recipient,
        "subject": email.subject,
        "body": email.body,
        "received_date": email.received_date.isoformat(),  # Convert to ISO format
        "is_read": email.is_read,
    }

    print(f"The email is: %s" % email)

    # Convert the dictionary to json
    payload_json = json.dumps(payload)
    # print(f"Payload json_data: {payload_json}")

    # Encode the json data to base64
    encoded_data = base64.b64encode(payload_json.encode()).decode("utf-8")
    # print(f"base64 data: {encoded_data}")

    complaint = {
        "channel": "chat",
        "timestamp": email.received_date.isoformat(),
        "session_id": "str(instance.session_id)",
        "message_id": str(email.id),
        "from": "str(instance.session_id)",
        "message": encoded_data,
        "mime": "appication/json",
    }

    try:
        # Send the POST request
        response = requests.post(api_url, json=complaint, headers=headers)
        print(f"API Response: {response.status_code}, {response.text}")
        response.raise_for_status()

        # if response.status_code == 201:
        #     # Parse the response JSON
        #     response_data = response.json()

        #     # # Extract the `messages[0][0]` value
        #     # message_id = response_data.get("messages", [[]])[0][0]

        #     # if message_id:
        #     #     # Save the `message_id` to the `message_id_ref` field
        #     #     instance.message_id_ref = message_id
        #     #     instance.save(update_fields=["message_id_ref"])
        #     #     logging.info(f"message_id_ref saved: {message_id}")
        #     # else:
        #     #     logging.error("message_id not found in API response.")
        # else:
        #     logging.error(
        #         f"API call failed with status: {response.status_code}, Response: {response.text}"
        #     )
    except requests.exceptions.RequestException as e:
        # Log error details
        logging.error(f"Failed to forward email: {email.subject}. Error: {e}")
        return None
