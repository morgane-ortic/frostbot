import simplematrixbotlib as botlib
import pandas as pd
import os
import requests
import time
from datetime import date, datetime, timedelta
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
    def __init__(self, loop_number, frost_detected):
        self.loop_number = loop_number
        self.frost_detected = frost_detected
        self.fetch_location_data()


    def fetch_location_data(self):
        load_dotenv()
        # You can either put the desired timezone, longitude and latitude in your local env file OR directly replace the following values
        self.timezone = os.getenv('TIMEZONE')
        self.latitude = os.getenv('LATITUDE')
        self.longitude = os.getenv('LONGITUDE')


    def sort_temps(self):
        '''keeps only freezing temperature in the next 48h'''
        self.below_zero = ""
        current_datetime = datetime.now().astimezone()
        time_limit = current_datetime + timedelta(hours=48)
        print(f'Evaluating temperatures until{time_limit}\n')
        print(f'The following temperatures are below the threshold:\n')
        for index, record in self.hourly_temp.items():
            if pd.to_datetime(record['date']) > time_limit:
                print(pd.to_datetime(record['date']))
        self.below_zero = {
            index: record
            for index, record in self.hourly_temp.items()
            if record['temperature_2m'] < self.reference_temp
            and pd.to_datetime(record['date']) - timedelta(seconds=3559) >= current_datetime
            and pd.to_datetime(record['date']) <= time_limit
        }


    def format_neg_temp(self):
        treated_dates = []
        self.formatted_temps = ''
        for record in self.below_zero.values():
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

        # Get the DataFrame from the API
        hourly_temp_df = check_temp(self.timezone, self.latitude, self.longitude)
        # Convert the 'date' column to desired timezone
        hourly_temp_df['date'] = pd.to_datetime(hourly_temp_df['date']).dt.tz_convert(self.timezone)
        # Convert the DataFrame to a dictionary
        self.hourly_temp = hourly_temp_df.to_dict(orient='index')

        self.reference_temp = 0 # in °C
        self.sort_temps()

        if self.below_zero:
            # Send warning only if no frost warning was sent in the last loop OR if 4 loops have already run
            if self.frost_detected != True or loop_number >= 4:
                self.frost_detected = True
                result_1 = (f'Temperatures below {self.reference_temp} °C detected:')
                # Format the records
                self.format_neg_temp()
                print(f'{result_1}{self.formatted_temps}')
                self.send_warning()
        else:
            self.frost_detected = False
            self.no_result = (f'No temperatures below {self.reference_temp} °C detected.')
            print(self.no_result)
        return (self.frost_detected)
    

    def send_warning(self):
        '''Send a message if temperatures below the reference temperature are detected'''

        print('Sending a warning...')
        homeserver = os.getenv('HOMESERVER')
        access_token = os.getenv('ACCESS_TOKEN')
        room_id = os.getenv('ROOMID')

        url = f"{homeserver}/_matrix/client/v3/rooms/{room_id}/send/m.room.message"

        message = f"Frost warning in the next 36 hours!{self.formatted_temps}"
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


def main(loop_number, frost_detected):
    frost_notifier = FrostNotifier(loop_number, frost_detected)
    frost_detected = frost_notifier.check_frost()
    return frost_detected

if __name__ == '__main__':
    loop_number = 0
    frost_detected = False
    print(f'''Number of loops: {loop_number}
Frost detected = {frost_detected}
          ''')
    while True:
        frost_detected = main(loop_number, frost_detected)
        loop_number += 1       
        # Reinitialize loop count every 4 times (default = 6*4 = 24 h)
        # If there was already a frost warning in the last 24 h, the next one will be sent 24 h later only
        if loop_number > 4:
            loop_number = 1            
        # Defines how often to check temperatures in seconds
        checking_interval = 6 * 60 * 60
        time.sleep(checking_interval)