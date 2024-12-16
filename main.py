import json
import simplematrixbotlib as botlib

from import_weather import check_temp

creds_file = 'creds.json'
timezone = "Europe/Berlin"

# def import_creds():
#     '''Import credentials from a json file'''
#     with open(creds_file, 'r') as file:
#         creds_data = json.load(file)
#     # unpacking each credential from the list
#     if isinstance(creds_data, list) and len(creds_data) == 3:
#         homeserver, username, password = creds_data
#     else:
#         raise ValueError("Unable to import credentials")
    
#     return homeserver, username, password

# # Call import_creds() function and unpack the returned values
# homeserver, username, password = import_creds()

# creds = botlib.Creds(homeserver, username, password)

hourly_dataframe = check_temp(timezone)

print(hourly_dataframe)