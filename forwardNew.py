##USE THIS CODE ONLY - LATEST AND WORKS

import imaplib
import email
import smtplib
import time
from email.message import EmailMessage
from email import policy
from email.parser import BytesParser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


def forward(hostName,hostMail,hostPassword,subject,playerList,playerMapping,VERBOSE=True,GIFT=False):
    if VERBOSE:
        print(playerList)
        print(playerMapping)
        print("Subject is "+subject)
    IMAP_HOST = "imap.gmail.com"
    SMTP_HOST = "smtp.gmail.com"
    SMTP_PORT = 587

    USERNAME = hostMail
    PASSWORD = hostPassword
    FORWARD_TIME_DELAY = 5
    EXCEPTION_TIME_DELAY = 60

    # Open IMAP connection
    imap_client = imaplib.IMAP4_SSL(IMAP_HOST)
    imap_client.login(USERNAME, PASSWORD)

    def fetchMessageIDs(FROM_ADDRESS,TO_ADDRESS):
        if VERBOSE:
            print("from "+FROM_ADDRESS+", to "+TO_ADDRESS)

        # Fetch messages' ID list
        status, _ = imap_client.select("INBOX", readonly=True)
        if status != "OK":
            raise Exception("Could not select connect to INBOX.")

        criterion = ""
        
        status, data = imap_client.search(None, 'SUBJECT "'+subject+'" FROM "'+FROM_ADDRESS+'"')
        if status != "OK":
            raise Exception("Could not search for emails.")

        messages_id_list = data[0].decode("utf-8").split(' ')
        if VERBOSE:
            print("{} messages were found. Forwarding will start immediately.".format(len(messages_id_list)))
            print("Messages ids: {}".format(messages_id_list))
            print()
        
        return messages_id_list

    def forwardMessages(messages_id_list,FROM_ADDRESS,TO_ADDRESS,fromName):
        # Fetch each message data
        messages_sent = []
        while len(messages_sent) < len(messages_id_list):
            msg_id = messages_id_list[len(messages_sent)]
            status, msg_data = imap_client.fetch(msg_id, '(RFC822)')

            raw_email = msg_data[0][1]
            msg = BytesParser(policy=policy.default).parsebytes(raw_email)

            forwarded_msg = MIMEMultipart()
            forwarded_msg['From'] = FROM_ADDRESS
            forwarded_msg['To'] = TO_ADDRESS
            if GIFT:
                forwarded_msg['Subject'] = subject+" from "+fromName
            else:
                forwarded_msg['Subject'] = subject

            # Separate text and HTML parts
            text_parts = []
            html_parts = []

            if msg.is_multipart():
                for part in msg.get_payload():
                    content_type = part.get_content_type().lower()
                    if content_type.startswith('text/html'):
                        html_parts.append(part.get_payload(decode=True).decode(part.get_content_charset()))
                        break
                    elif content_type.startswith('text/plain'):
                        text_parts.append(part.get_payload(decode=True).decode(part.get_content_charset()))
                        break
            else:
                # If the email is not multipart, consider it as text/plain
                text_parts.append(msg.get_payload(decode=True).decode(msg.get_content_charset()))

            # Attach text part
            if text_parts:
                text_part = MIMEText('\n'.join(text_parts), _subtype='plain')
                forwarded_msg.attach(text_part)

            # Attach HTML part
            if html_parts:
                html_part = MIMEText('\n'.join(html_parts), _subtype='html')
                forwarded_msg.attach(html_part)

            # Copy attachments
            for part in msg.iter_attachments():
                if not isinstance(part, email.message.Message):
                    # Only attach non-multipart parts (attachments)
                    attachment = MIMEBase(*part.get_content_type().split('/'))
                    attachment.set_payload(part.get_payload(decode=True))
                    encoders.encode_base64(attachment)
                    attachment.add_header('Content-Disposition', f'attachment; filename="{part.get_filename()}"')
                    forwarded_msg.attach(attachment)

            if status != "OK":
                raise Exception("Could not fetch email with id {}".format(msg_id))

            try:
                # Open SMTP connection
                smtp_client = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
                smtp_client.starttls()
                smtp_client.ehlo()
                # smtp_client.set_debuglevel(1)
                smtp_client.login(USERNAME, PASSWORD)

                # Send message
                smtp_client.send_message(forwarded_msg)
                messages_sent.append(msg_id)
                if VERBOSE:
                    print("Message {} was sent. {} emails from {} emails were forwarded.".format(msg_id,
                                                                                                    len(messages_sent),
                                                                                                    len(messages_id_list)))

                # Close SMTP connection
                smtp_client.close()

                # Time delay until next command
                time.sleep(FORWARD_TIME_DELAY)
            except smtplib.SMTPSenderRefused as exception:
                if VERBOSE:
                    print("Encountered an error! Error: {}".format(exception))
                    print("Messages sent until now:")
                    print(messages_sent)
                    print("Time to take a break. Will start again in {} seconds.".format(EXCEPTION_TIME_DELAY))
                time.sleep(EXCEPTION_TIME_DELAY)
            except smtplib.SMTPServerDisconnected as exception:
                if VERBOSE:
                    print("Server disconnected: {}".format(exception))
            except smtplib.SMTPNotSupportedError as exception:
                if VERBOSE:
                    print("Connection failed: {}".format(exception))
                    print("Messages sent until now:")
                    print(messages_sent)
                    print("Time to take a break. Will start again in {} seconds.".format(EXCEPTION_TIME_DELAY))
                time.sleep(EXCEPTION_TIME_DELAY)
            except smtplib.SMTPDataError:
                raise Exception("Daily user sending quota exceeded.")

        if VERBOSE:
            print("Job done. Enjoy your day!")


    for player in playerList:
        santee = playerList[player]
        santa = playerList[playerMapping[player]]
        forwardMessages(fetchMessageIDs(santee,santa),santee,santa,player)
    # Logout
    imap_client.close()
    imap_client.logout()