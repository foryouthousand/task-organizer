import os
import google.auth
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/tasks']

def main():
    """Shows basic usage of the Google Tasks API.
    Creates a Google Tasks API service and fetches the task lists.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens.
    if os.path.exists('token.json'):
        creds = google.auth.load_credentials_from_file('token.json', SCOPES)[0]
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)

        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # Build the service
    service = build('tasks', 'v1', credentials=creds)

    # Call the Tasks API
    results = service.tasklists().list().execute()
    tasklists = results.get('items', [])

    if not tasklists:
        print('No task lists found.')
    else:
        print('Task Lists:')
        for tasklist in tasklists:
            print(f"{tasklist['title']} (ID: {tasklist['id']})")

if __name__ == '__main__':
    main()