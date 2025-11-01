from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

from dotenv import load_dotenv
load_dotenv()

# Load credentials
creds = service_account.Credentials.from_service_account_file(
    "credentials/custom_search_credentials.json",
    scopes=["https://www.googleapis.com/auth/cse"]
)

# Use your CSE API
service = build("customsearch", "v1", credentials=creds)

result = service.cse().list(
    q="women cricket world cup final",
    cx=os.getenv("CUSTOM_SEARCH_ENGINE_ID")
).execute()

for item in result.get("items", []):
    print(item)
    break
