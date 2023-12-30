import smtplib
from email.mime.text import MIMEText 
from email import encoders 
import time
def sendInvites(sender,password,playerList,inviteText,subject,VERBOSE=True,recipientList={}):
    FORWARD_TIME_DELAY = 5
    EXCEPTION_TIME_DELAY = 60
    try:
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(sender, password)
        print("Sending mails...")
        for player in playerList:
            recipient=""
            if len(recipientList)!=0:
                recipient = recipientList[player]
            message = MIMEText(inviteText.replace("##Name##",player).replace("##RecipientName##",recipient),"plain")
            message["FROM"] = sender
            message["SUBJECT"] = subject
            s.sendmail(sender,playerList[player],message.as_string())
        s.quit()
        print("Mails have been sent!")
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