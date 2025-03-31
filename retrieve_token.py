import requests
import os
from dotenv import load_dotenv

# Load credentials from .env file
load_dotenv()
HOMESERVER = os.getenv('HOMESERVER')
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')

def get_access_token(homeserver, username, password):
    '''
    Authenticate with the Matrix homeserver and retrieve an access token.
    '''
    url = f'{homeserver}/_matrix/client/v3/login'
    payload = {
        'type': 'm.login.password',
        'user': username,
        'password': password
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        # Return the access token from the response
        return response.json()['access_token']
    else:
        # Raise an error if the login fails
        raise Exception(f'Failed to log in: {response.status_code} {response.json()}')

if __name__ == '__main__':
    try:
        # Get the access token
        token = get_access_token(HOMESERVER, USERNAME, PASSWORD)
        print(f'Access token: {token}')
    except Exception as e:
        print(f'An error occurred: {e}')