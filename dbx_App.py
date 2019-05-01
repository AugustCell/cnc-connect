import dropbox

auth_token = "eSp1cKEzdOAAAAAAAAAAFHo3_k2buR70MgbGUlJ0vUGBmyIC1YfW05u2b6AS6M6R"

dbx = dropbox.Dropbox(auth_token)

#This uploads a file from local to dropbox
#with open('pip_install.py', 'rb') as f:
#    dbx.files_upload(f.read(), '/pip_install.py')

#This downloads a file from dropbox to local
with open("test.py", "w") as f:
    metadata, res = dbx.files_download(path="/pip_install.py")
    f.write((res.content).decode())