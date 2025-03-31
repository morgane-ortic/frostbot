import simplematrixbotlib as botlib
import pandas as pd
import os
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
    def __init__(self, timezone, frost_bot):
        self.timezone = timezone
        self.frost_bot = frost_bot


    def format_neg_temp(self, records):
        for record in records.values():
            record['date'] = pd.to_datetime(record['date']).strftime('%d-%m-%Y %H:%M')
            record['temperature_2m'] = round(record['temperature_2m'], 1)
        return records


    def check_frost(self):
        '''Get the temperatures and check whether they are below the reference temperature'''
        self.frost_datetimes = ''
        # Get the DataFrame and reset the index to include it as a column
        self.hourly_temp = check_temp(self.timezone).to_dict(orient='index')
        reference_temp = 5 # in °C
        below_zero = {index: record for index, record in self.hourly_temp.items() if record['temperature_2m'] < reference_temp}

        if below_zero:
            result_1 = (f'Temperatures below {reference_temp} detected:')
            # Format the records
            formatted_below_zero = self.format_neg_temp(below_zero)
            for index, record in formatted_below_zero.items():
                self.frost_datetimes += (f'Date: {record['date']}, Temperature: {record['temperature_2m']}\n')
                print(self.frost_datetimes)
        else:
            self.no_result = (f'No temperatures below {reference_temp} detected.')
            print(self.no_result)
    
    def send_warning():
        print('Testing the bot')
        '''Send a message if temperatures below the reference temperature are detected'''




def main():

    frost_bot = init_bot()

    frost_notifier = FrostNotifier('Europe/Berlin', frost_bot)
    frost_notifier.check_frost()

    @frost_bot.listener.on_message_event
    def on_message(event):
        frost_notifier.send_warning(event)
    
    frost_bot.run()

if __name__ == '__main__':
    main()