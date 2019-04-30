import dropbox

auth_token = "eSp1cKEzdOAAAAAAAAAADFTKh7tVMADzEWVmHJ8Q-aOwZQcT1993aavHJF6Nwvdk"

dbx = dropbox.Dropbox(auth_token)

#This uploads a file from local to dropbox
with open('comm.py', 'rb') as f:
    dbx.files_upload(f.read(), '/malicious.py')

#This downloads a file from dropbox to local
with open("test.py", "w") as f:
    metadata, res = dbx.files_download(path="/malicious.py")
    f.write((res.content).decode())