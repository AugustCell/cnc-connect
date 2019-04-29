import os
import smtplib
import imaplib
import email

email = "os.services.updates@gmail.com"
password = "cse363esc"
SMTP_SERVER = "imap.gmail.com"
SMTP_PORT = 587

def readEmail():
    try:
        mail = imaplib.IMAP4_SSL(SMTP_SERVER)
        mail.login(email, password)
        mail.select('inbox')

        type, data = mail.search(None, 'ALL')
        mailId = data[0]

        idList = mailId.split()
        firstEmail = int(idList[0])
        latestEmail = int(idList[0])

        for i in range(latestEmail,firstEmail, -1):
            typ, data = mail.fetch(i, '(RFC822)' )

            for response in data:
                if isinstance(response, tuple):
                    msg = email.message_from_string(response[1])
                    subject = msg['subject']
                    sender = msg['from']
                    print ('From : ' + sender + '\n')
                    print ('Subject : ' + subject + '\n')

    except Exception as e:
        print (str(e))
