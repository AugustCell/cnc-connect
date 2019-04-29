import os
import smtplib
import imaplib
import email

email = "os.services.updates@gmail.com"
password = "cse363esc"
SMTP_SERVER = "imap.gmail.com"
SMTP_PORT = 993

def readEmail():
    try:
        mail = imaplib.IMAP4_SSL(SMTP_SERVER)
        mail.login(email, password)
        mail.select('inbox')

        type, data = mail.search(None, 'ALL')
        mailId = data[0]

        '''
        idList = mailId.split()
        firstEmail = int(idList[0])
        latestEmail = int(idList[-1])
        '''
        
        for i in mailId.split():
            typ, data = mail.fetch(i, '(RFC822)' )
            msg = email.message_from_string(data[0][1])
            subject = msg['subject']
            sender = msg['from']
            print ('From : ' + sender + '\n')
            print ('Subject : ' + subject + '\n')

    except Exception as e:
        print (str(e))

readEmail()
