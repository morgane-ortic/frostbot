import json
import simplematrixbotlib as botlib
import pandas as pd
from import_weather import check_temp

creds_file = 'creds.json'

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

class FrostBot():
    def __init__(self, timezone):
        self.timezone = timezone


    def format_neg_temp(self, records):
        for record in records.values():
            record['date'] = pd.to_datetime(record['date']).strftime('%d-%m-%Y %H:%M')
            record['temperature_2m'] = round(record['temperature_2m'], 1)
        return records


    def check_frost(self):
        # Get the DataFrame and reset the index to include it as a column
        self.hourly_temp = check_temp(self.timezone).to_dict(orient='index')
        
        below_zero = {index: record for index, record in self.hourly_temp.items() if record['temperature_2m'] < 8}

        if below_zero:
            print("Temperatures below 0 detected:")
            # Format the records
            formatted_below_zero = self.format_neg_temp(below_zero)
            for index, record in formatted_below_zero.items():
                print(f"Date: {record['date']}, Temperature: {record['temperature_2m']}")
        else:
            print("No temperatures below 0 detected.")


def main():
    frost_bot = FrostBot("Europe/Berlin")
    frost_bot.check_frost()


if __name__ == "__main__":
    main()