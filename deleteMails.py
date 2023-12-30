#WORKS!

import imaplib
import email
from email.header import decode_header

def delete(hostName,hostMail,hostPassword,subject,mailType="INBOX",VERBOSE=True):
    print("deleting from "+mailType+" with subject = "+subject)
    IMAP_HOST = "imap.gmail.com"
    USERNAME = hostMail
    PASSWORD = hostPassword
    SEARCH_CRITERIA = 'SUBJECT "'+subject+'"'

    # Open IMAP connection
    imap_client = imaplib.IMAP4_SSL(IMAP_HOST)
    imap_client.login(USERNAME, PASSWORD)

    # Fetch messages' ID list
    status, _ = imap_client.select(mailType, readonly=False)  # Set readonly to False to mark emails as deleted
    if status != "OK":
        raise Exception("Could not select connect to "+mailType)

    status, data = imap_client.search(None, SEARCH_CRITERIA)
    if status != "OK":
        raise Exception("Could not search for emails.")

    messages = data[0].decode("utf-8").split(' ')

    if VERBOSE:
        print("{} messages were found. Deleting will start immediately.".format(len(messages)))
        print("Messages ids: {}".format(messages))
        print()

    for mail_id in messages:
        if mail_id=='':
            return
        _, msg_data = imap_client.fetch(mail_id, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])

                # Decode the email subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding or 'utf-8')

                print("Deleting:", subject)

        # Mark the mail as deleted
        imap_client.store(mail_id, "+FLAGS", "\\Deleted")

    # Expunge to permanently remove deleted emails
    imap_client.expunge()

    # Close the mailbox
    imap_client.close()

    # Logout from the account
    imap_client.logout()
