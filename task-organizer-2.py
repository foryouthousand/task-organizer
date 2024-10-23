import os
import google.auth
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/tasks']

def get_tasks(service, task_list_id):
    """Retrieve tasks for the given task list ID."""
    tasks = service.tasks().list(tasklist=task_list_id).execute()
    return tasks.get('items', [])

def sort_tasks(tasks):
    not_sorted_tasks = []

    for task in tasks:
        task_title = task['title']
        if "HIGH-" in task_title:
            not_sorted_tasks.append({'title':task_title, 'priority':4})
        elif "MED-" in task_title:
            not_sorted_tasks.append({'title':task_title, 'priority':3})
        elif "LOW-" in task_title:
            not_sorted_tasks.append({'title':task_title, 'priority':2})
        else:
            not_sorted_tasks.append({'title':task_title, 'priority':1})
    # priority_order = {'HIGH': 1, 'MED': 2, 'LOW': 3}    
    return sorted(not_sorted_tasks, key=lambda x: x['priority'])

def replace_tasks(service, task_list_id, sorted_tasks):
    """Replace existing tasks in the task list with the sorted tasks."""
    # Step 1: Fetch existing tasks
    existing_tasks = service.tasks().list(tasklist=task_list_id).execute().get('items', [])

    # Step 2: Delete existing tasks
    for task in existing_tasks:
        service.tasks().delete(tasklist=task_list_id, task=task['id']).execute()

    # # Step 3: Add sorted tasks
    for task in sorted_tasks:
        # You can customize the task structure here if needed
        new_task = {'title': task['title']}
        service.tasks().insert(tasklist=task_list_id, body=new_task).execute()


def main():
    """Shows basic usage of the Google Tasks API.
    Creates a Google Tasks API service and fetches the task lists.
    """

    list_name = input('Input list to order')


    creds = None
    # The file token.json stores the user's access and refresh tokens.
    # if os.path.exists('token.json'):
    #     creds = google.auth.load_credentials_from_file('token.json', SCOPES)[0]
    
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
            if  tasklist['title'] == list_name:
                print()
                print(tasklist['title'])
                tasks = get_tasks(service, tasklist['id'])
                sorted_tasks = sort_tasks(tasks)
                replace_tasks(service, tasklist['id'], sorted_tasks)
                for task in sorted_tasks:
                    print(task['title'])
            # print(f"{tasklist['title']} (ID: {tasklist['id']})")
            else:
                print(f'could not find {list_name}')

if __name__ == '__main__':
    main()