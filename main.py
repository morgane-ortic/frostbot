import json
import simplematrixbotlib as botlib

creds_file = 'creds.json'

def import_creds():
    '''Import credentials from a json file'''
    with open(creds_file, 'r') as file:
        creds_data = json.load(file)
    # unpacking each credential from the list
    if isinstance(creds_data, list) and len(creds_data) == 3:
        homeserver, username, password = creds_data
    else:
        raise ValueError("Unable to import credentials")
    
    return homeserver, username, password

# Call import_creds() function and unpack the returned values
homeserver, username, password = import_creds()

creds = botlib.Creds(homeserver, username, password)