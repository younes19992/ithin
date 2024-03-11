import requests
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# Path to your service account key file
SERVICE_ACCOUNT_FILE = r'C:\Users\YOUNES CHERRADI\Desktop\roblox api download\client_secrets.json'

# Define Google Drive API scopes
SCOPES = ['https://www.googleapis.com/auth/drive']

# Discord webhook URL
DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1216548507822067773/Fvzm1Ek8vnww-m3Mc_1-b5RhkNrmxEfwjykMZEubkgsuK254uZ3X9FWeFSd7wr_s1Hnx'

def get_credentials():
    """Retrieve credentials."""
    return service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

def build_drive_service():
    """Build Google Drive service."""
    return build('drive', 'v3', credentials=get_credentials())

def send_discord_message(message):
    """Send a message to Discord webhook."""
    payload = {'content': message}
    requests.post(DISCORD_WEBHOOK_URL, json=payload)

def create_folder(folder_name):
    """Create a new folder in Google Drive."""
    drive_service = build_drive_service()
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    try:
        folder = drive_service.files().create(body=file_metadata, fields='id').execute()
        folder_id = folder.get('id')
        print(f"Folder '{folder_name}' created successfully.")
        return folder_id
    except HttpError as e:
        print(f"An error occurred: {e}")
        send_discord_message(f"Failed to create folder '{folder_name}': {e}")
        return None

def upload_file(file_path, custom_file_name=None, folder_name=None):
    """Upload a file to Google Drive."""
    drive_service = build_drive_service()

    # If custom file name is provided, use it, else use original file name
    if custom_file_name:
        file_name = custom_file_name
    else:
        file_name = os.path.basename(file_path)

    file_metadata = {'name': file_name}
    
    # Get or create folder ID if folder name is provided
    if folder_name:
        folder_id = get_folder_id(folder_name)
        if folder_id is None:
            folder_id = create_folder(folder_name)
            if folder_id is None:
                return None
        file_metadata['parents'] = [folder_id]

    media_body = MediaFileUpload(file_path, resumable=True)

    try:
        # Upload the file directly without specifying a file ID
        file = drive_service.files().create(body=file_metadata, media_body=media_body, fields='id,webViewLink').execute()
        file_id = file.get('id')
        file_url = file.get('webViewLink')
        if file_id:
            send_discord_message(f"User '{file_name}' uploaded successfully! User File URL: {file_url}")
        return file_id
    except HttpError as e:
        print(f"An error occurred: {e}")
        send_discord_message(f"Failed to upload file '{file_name}': {e}")
        return None

def make_public(file_id):
    """Make a file publicly accessible."""
    drive_service = build_drive_service()

    permission = {
        'type': 'anyone',
        'role': 'reader',
    }

    try:
        # Set the permissions for the file to be publicly accessible
        drive_service.permissions().create(fileId=file_id, body=permission).execute()
        print('File is now public.')
    except HttpError as e:
        print(f"An error occurred: {e}")
        send_discord_message(f"Failed to make file public: {e}")

def get_folder_id(folder_name):
    """Get the folder ID based on its name."""
    drive_service = build_drive_service()
    folder_query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    folders = drive_service.files().list(q=folder_query, fields='files(id)').execute().get('files', [])
    if folders:
        return folders[0]['id']
    else:
        return None
