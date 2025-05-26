import os
import firebase_admin
from firebase_admin import credentials, auth

# Get the current script directory
current_dir = os.path.dirname(__file__)

# Go to the parent directory (project/)
project_dir = os.path.abspath(os.path.join(current_dir, os.pardir))

# Build full path to data.txt
file_path = os.path.join(project_dir, 'serviceAccountKey.json')

# service_account_path = r'C:\Users\user\OneDrive\Desktop\Tonmoy\Projects\Client 08 [VPN-App Integration]\vpn-backend\serviceAccountKey.json'
cred = credentials.Certificate(file_path)
firebase_admin.initialize_app(cred)

def verify_token(id_token):
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        return None
