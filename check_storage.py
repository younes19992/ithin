from google.oauth2 import service_account
from googleapiclient.discovery import build

# Path to your service account key file
SERVICE_ACCOUNT_FILE = r'C:\Users\YOUNES CHERRADI\Desktop\roblox api download\client_secrets.json'

# Define Google Drive API scopes
SCOPES = ['https://www.googleapis.com/auth/drive']


def bytes_to_gb(bytes_value):
    return round(bytes_value / (1024 ** 3), 2)  # Convert bytes to gigabytes

def get_drive_storage():
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    drive_service = build('drive', 'v3', credentials=credentials)

    about = drive_service.about().get(fields='storageQuota').execute()
    storage_quota = about['storageQuota']

    total_storage = bytes_to_gb(int(storage_quota.get('limit', 0)))
    used_storage = bytes_to_gb(int(storage_quota.get('usage', 0)))
    available_storage = bytes_to_gb(int(storage_quota.get('limit', 0)) - int(storage_quota.get('usage', 0)))

    return total_storage, used_storage, available_storage

if __name__ == '__main__':
    total_storage, used_storage, available_storage = get_drive_storage()
    print(f'Total Storage: {total_storage} GB')
    print(f'Used Storage: {used_storage} GB')
    print(f'Available Storage: {available_storage} GB')
