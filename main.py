# ePaperWeatherStation by Frederik Andersen
# v.2.0.0
# Date 2025-02-07
# This project fetches weather data for a specified location using the MET Weather API
# and displays it on a Waveshare 5.65-inch ePaper display. The weather data is updated
# every hour, and the screen is cleared once every 24 hours to prevent ghosting.
# Released under the MIT License (MIT). See LICENSE for details.

import utime
import gc
import machine
from datafetcher import DataFetcher
from timemanager import TimeManager
import user_input
from screenmanager import ScreenManager                                                                    


def run():
    # The location is set in user_input.py. It must be defined in datafetcher locations dictionary with latitude, longitude and altitude
    data = DataFetcher(user_input.LOCATION)  
    time_manager = TimeManager(data)
    screen_manager = ScreenManager(data, time_manager)
    
    while True:
        time_manager.sync_time_if_needed() # Once a day, keeps the clock correct.
        time_for_update = time_manager.is_it_time()
        if time_for_update[0] == True: # Time to fetch new weather data?
            print(f'Updating the weather data. Datetime: {time_manager.rtc.datetime()}')
            try:
                data.fetch_new_weather_data() # Update the data
            except Exception as e:
                print(f'Fetch failed: {e}')
                utime.sleep(300) # Wait 5 minutes before trying again.
            
        else:
            if time_for_update[2] == True: # Time to clear the screen? Should be at night
                print(f'Cleaning the screen. Datetime: {time_manager.rtc.datetime()}')
                screen_manager.clear()
                screen_manager.clear()
                
            elif time_for_update[1] == True: # Time to update the screen?
                print(f'Updating the screen. Datetime: {time_manager.rtc.datetime()}')
                screen_manager.draw() # Draw the screen

        gc.collect() # Free up memory.
        utime.sleep(10)


if __name__=='__main__':
    try:
        run()
    except Exception as e: # Ctrl+C in Thonny is not an Exception, so it still stops the program.
        print(f'Fatal error: {e}')
        utime.sleep(300) # Wait 5 minutes so the screen is not redrawn too often.
        machine.reset() # Full restart. main.py starts again by itself.
