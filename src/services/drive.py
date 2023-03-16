from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

gauth = GoogleAuth()       
gauth.LocalWebserverAuth()    
drive = GoogleDrive(gauth)  

# Set the folder name you want to check for or create
folder_name = 'fu-detect-data'

# Query the Drive API for folders with the given name
query = f"mimeType='application/vnd.google-apps.folder' and trashed=false and title='{folder_name}'"
folders = drive.ListFile({'q': query}).GetList()

if len(folders) == 0:
    # No folder with the given name exists, create a new folder
    folder_metadata = {'title': folder_name, 'mimeType': 'application/vnd.google-apps.folder'}
    folder = drive.CreateFile(folder_metadata)
    folder.Upload()

    # Get the folder ID of the newly created folder
    folder_parent_id = folder['id']
else:
    # A folder with the given name already exists, get its ID
    folder_parent_id = folders[0]['id']
