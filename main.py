import simplematrixbotlib as botlib
import pandas as pd
import os
import requests
import time
from datetime import date, timedelta
from dotenv import load_dotenv
from import_weather import check_temp


def init_bot():

    load_dotenv()
    homeserver = os.getenv('HOMESERVER')
    username = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')

    creds = botlib.Creds(homeserver, username, password)

    frost_bot = botlib.Bot(creds)
    return frost_bot
    

class FrostNotifier():
    def __init__(self):
        self.fetch_location_data()


    def fetch_location_data(self):
        load_dotenv()
        # You can either put the desired timezone, longitude and latitude in your local env file OR directly replace the following values
        self.timezone = os.getenv('TIMEZONE')
        self.latitude = os.getenv('LATITUDE')
        self.longitude = os.getenv('LONGITUDE')


    def format_neg_temp(self, records):
        treated_dates = []
        self.formatted_temps = ''
        for record in records.values():
            record['time'] = pd.to_datetime(record['date']).strftime('%H:%M')
            record['temperature_2m'] = round(record['temperature_2m'], 1)
            record['date'] = pd.to_datetime(record['date']).strftime('%A %d.%m')
            if record['date'] not in treated_dates:
                treated_dates.append(record['date'])
                self.formatted_temps += f'\n\n{record['date']}:\n\n'
            self.formatted_temps += f'      {record['time']}: {record['temperature_2m']} °C\n'


    def check_frost(self):
        '''Get the temperatures and check whether they are below the reference temperature'''
        self.formatted_temps = ''
        # Get the DataFrame and reset the index to include it as a column
        self.hourly_temp = check_temp(self.timezone, self.latitude, self.longitude).to_dict(orient='index')
        reference_temp = 0 # in °C
        below_zero = {index: record for index, record in self.hourly_temp.items() if record['temperature_2m'] < reference_temp}

        if below_zero:
            result_1 = (f'Temperatures below {reference_temp} detected:')
            # Format the records
            self.format_neg_temp(below_zero)
            print(f'{result_1}{self.formatted_temps}')
            self.send_warning()
        else:
            self.no_result = (f'No temperatures below {reference_temp} detected.')
            print(self.no_result)
    

    def send_warning(self):
        '''Send a message if temperatures below the reference temperature are detected'''
        print('Sending a warning...')
        homeserver = os.getenv('HOMESERVER')
        access_token = os.getenv('ACCESS_TOKEN')
        room_id = os.getenv('ROOMID')

        url = f"{homeserver}/_matrix/client/v3/rooms/{room_id}/send/m.room.message"

        message = f"Frost warning in the next 48 hours!{self.formatted_temps}"
        payload = {
            "msgtype": "m.text",
            "body": message
        }

        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            print(f"Message sent to room {room_id}: {message}")
        else:
            print(f"Failed to send message: {response.status_code}, {response.json()}")


def main():
    frost_notifier = FrostNotifier()
    frost_notifier.check_frost()

if __name__ == '__main__':
    while True:
        main()
        time.sleep(6 * 60 * 60)