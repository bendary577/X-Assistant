from __future__ import print_function
import sys
import os.path
import google.auth
from win10toast import ToastNotifier
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

''' ------------ this section is for defining global variables -------'''
# If modifying these scopes, delete the file token.json.
SCOPES = [
'https://www.googleapis.com/auth/drive.file',
'https://www.googleapis.com/auth/drive.resource',
]

''' ------------------ this section is for defining classes ----------------'''
class Article :
    link = ""
    is_read = False
  
    def __init__(self, link, is_read):
        self.link = link
        self.is_read = is_read
  
''' ------------------- this section is for defining methods -------------------- '''  
#this method send reminder notification to windows
def send_widnows_notification() : 
    toast = ToastNotifier()
    toast.show_toast(
        "Notification",
        "Notification body",
        duration = 20,
        icon_path = "icon.ico",
        threaded = True)
    
#this method authenticates the credentials to google drive
def authenticate_to_google_drive():
    """Shows basic usage of the Drive v3 API.
    Authentication
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

#this method list files in google drive      
def google_drive_list_files():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = authenticate_to_google_drive()
    try:
        service = build('drive', 'v3', credentials=creds)
        # Call the Drive v3 API
        results = service.files().list(
            pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])
        
        if not items:
            print('No files found.')
            return
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')
        
#this method search for files in google drive      
def google_drive_search_folder(folder_name):
    """Search file in drive location
    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """
    creds = authenticate_to_google_drive()
    try:
        #create drive api client
        service = build('drive', 'v3', credentials=creds)
        folders = []
        page_token = None
        response = service.files().list(q="name = '" + folder_name + "'",
                                    spaces='drive',
                                    fields='nextPageToken, '
                                           'files(id, name)',
                                    pageToken=page_token).execute()
        found_folders = response.get('files', [])
        folder_len = len(found_folders)
        if folder_len > 0 :
            for folder in found_folders:
                # Process change
                print(F'Found Folder: {folder.get("name")}, {folder.get("id")}')
                folders.extend(response.get('files', []))
                page_token = response.get('nextPageToken', None)
                if page_token is None:
                    break
        else :
            print(F'We didn\'t find the folder you\'re searching for')

    except HttpError as error:
        print(F'An error occurred: {error}')

    return folders 
    
#this method search for files in google drive      
def google_drive_create_folder(folder_name):
    """ Create a folder and prints the folder ID
    Returns : Folder Id

    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """
    creds = authenticate_to_google_drive()
    try:
        # create drive api client
        service = build('drive', 'v3', credentials=creds)
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }

        # pylint: disable=maybe-no-member
        file = service.files().create(body=file_metadata, fields='id'
                                      ).execute()
        print(F'Folder ID: "{file.get("id")}".')
        return file.get('id')

    except HttpError as error:
        print(F'An error occurred: {error}')
    return None

def google_drive_upload_file_to_folder():
    print("google_drive_upload_file_to_folder")

''' ------------------- main method : program entry point ------------------------- ''' 
def main():
    script_passed_arguments_length = len(sys.argv)
    if script_passed_arguments_length < 2 :
        print(F'Arguments Number is not enough')
    else :
        script_name = sys.argv[0]
        script_operation = sys.argv[1]
        #--------- article reminder -------------
        if script_operation == "-ar" : 
            saved_articles = []
            for i in range(2, script_passed_arguments_length):
                print(sys.argv[i], end = " ")
                article = Article(sys.argv[i], False)
                saved_articles.append(article)
            print(len(saved_articles))
        #--------- google drive -------------
        elif script_operation == "-gd" :
            folders = google_drive_search_folder("X-Assistant-Work")
            if len(folders) == 0 :
                google_drive_create_folder("X-Assistant-Work")
            else : 
                google_drive_upload_file_to_folder()
        else :
            raise Exception 

    
if __name__ == '__main__':
    main()

"""
Execution Steps :
    1 - shift button + right click on the script folder
    2 - press (open PowerShell window here)
    3 - type (python Assistant.py -ar "https://www.article1.com")
"""

"""
Help : 
    1 - ar : article reminder
    2 - gds : google drive synch
"""   

"""
Algorithm :
    1 - pass article link to the script
    2 - save this article info in a list 
    3 - periodically call this script to run 
    4 - when the script run, choose a random article 
    5 - notify me for the article through windows notif.
"""

"""
Instalations :
    1 - pip install win10toast
    2 - pip install pybluez
    3 - pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
"""