# TimeManager by Frederik Andersen
# Class to handle all time-related functionalities.
# Requires an instance of DataFetcher.
# Released under the MIT License (MIT). See LICENSE for details.

import utime
import machine
import random
from ntptime import settime

class TimeManager():
    
    rtc = machine.RTC()
    
    def __init__(self, datafetcher):
        """
        Initialize the TimeManager with a DataFetcher instance.

        Parameters:
        datafetcher (DataFetcher): An instance of DataFetcher to get when weather data is expired.
        """
        self._summertime = 2 # Hours ahead of UTC/GMT
        self._wintertime = 1 # Hours ahead of UTC/GMT
        self._update_times = {'screen_update': None, 'screen_cleaned': False} # Dict for handeling update times.
        self._set_time()
        self._random_delay = random.randint(0, 60) # Used for adding random delay to expire time.
        
        self._datafetcher = datafetcher
        self._screen_cleanded = False # Bool to ensure cleaning only happen once at 2am.
        
    def _set_time(self):
        """
        Set time on RTC using ntptime settime.

        Raises:
        Exception: If the time could not be set.
        """
        try:
            settime()
        except Exception as e:
            exception_string = f"Could not set time: {e}"
            ErrorHandler(exception_string)
            raise
            

    def _get_time_difference(self):
        """
        Check if it's summer or wintertime.

        Returns:
        int: Hours ahead or behind UTC/GMT.
        """
        # Not made yet, todo.
        return self._wintertime
    
    def _is_weatherdata_expired(self):     
        """
        Check if the expire time for weather data is reached.
        A delay to actual time is added to ensure data traffic to the API is randomly timed.

        Returns:
        bool: True if time is expired, else False.
        """
        expire_time = self._datafetcher.get_expiretime_weatherdata().split(' ') # Get expire time.
        # Map month short to numbers.
        month_map = {
            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
            'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
        }
        
        # Parse the expire time list to get the date and time.
        day = int(expire_time[1])
        month_str = expire_time[2]
        year = int(expire_time[3])
        time_str = expire_time[4]
        month = month_map[month_str]
        
        # Parse the time string to get hour, minute, and second.
        hour, minute, second = map(int, time_str.split(':'))
        
        # Add a random delay of 0 to 60 minutes to the expire time.
        minute += self._random_delay
        
        # Handle overflow of minutes and hours.
        if minute >= 60:
            extra_hours = minute // 60
            minute = minute % 60
            hour += extra_hours
        
        if hour >= 24:
            extra_days = hour // 24
            hour = hour % 24
            day += extra_days # Can make a day in a month that does not exist, but no issue for function.
        
        # Create a tuple for the expire time with delay.
        expire_time_with_delay = (year, month, day, hour, minute)
        
        # Get the current time from the RTC.
        current_rtc_time = self.rtc.datetime()
        
        # Year, month, day, hour, minute.
        current_time_tuple = (current_rtc_time[0], current_rtc_time[1], current_rtc_time[2], current_rtc_time[4], current_rtc_time[5]) # Year, month, day, hour, minute.
        
        if current_time_tuple >= expire_time_with_delay: # Needed for updating to a new random delay.
            print(f"Current time: {current_time_tuple}, Expire time with delay: {expire_time_with_delay}, Raw expire time: {self._datafetcher.get_expiretime_weatherdata()}")
            self._random_delay = random.randint(0, 60) # Update the random delay for next time.
            
        return current_time_tuple >= expire_time_with_delay
    
    def get_datetime(self):
        """
        Get the current date and time in a human-readable format.

        Returns:
        list: A list containing [Weekday, day, month, year, hour, minute].
        """
        day_converter = {0: 'Mandag', 1: 'Tirsdag', 2: 'Onsdag', 3: 'Torsdag', 4: 'Fredag', 5: 'Lørdag', 6: 'Søndag'} # For converting rtc to human.
        month_converter = {1: 'Januar', 2: 'Februar', 3: 'Mars', 4: 'April', 5: 'Mai', 6: 'Juni',
                           7: 'Juli', 8: 'August', 9: 'September', 10: 'Oktober', 11: 'November', 12: 'Desember'} # For converting rtc to human.
        
        time_difference = self._get_time_difference()
            
        rtc_date = self.rtc.datetime()
        hour = rtc_date[4] + time_difference
        minute = rtc_date[5]
        
        if len(str(hour)) < 2: # If hour is less than 2 numbers, add a 0 in front.
            hour = f"0{hour}"
        elif hour == 24: # Show 00 instead of 24
            hour = "00"
        
        if len(str(minute)) < 2: # If minute is less than 2 numbers, add a 0 in front.
            minute = f"0{minute}"
            
        datetime = [day_converter[rtc_date[3]], rtc_date[2], month_converter[rtc_date[1]], rtc_date[0], hour, minute] # Weekday, day, month, year, hour, minute
        return datetime
    
    def get_time_with_delta(self, time_delta):
        """
        Returns the current hour adjusted by a specified time delta.

        Parameters:
        time_delta (int): The number of hours to add to the current hour.

        Returns:
        str: The adjusted hour in HH format.
        """
        now = self.get_datetime()[4]
        requested_time = int(now) + time_delta
        
        if requested_time >= 24:
            requested_time -= 24
        
        if len(str(requested_time)) < 2: # If hour is less than 2 numbers, add a 0 in front.
            requested_time = f"0{requested_time}"
        elif requested_time == 24: # Show 00 instead of 24
            requested_time = "00"
        
        return requested_time
        
    
    def is_it_time(self):
        """
        Check if it's time to update the screen, download new weather data, or clear the screen.
        - Screen should be updated every hour.
        - Data should be fetched when the data expires.
        - Screen should be cleared once every 24 hours.

        Returns:
        list: A list containing [fetch new weather_data, do a screen update, clear the screen].
        """
        response = [False, False, False] # response for [fetch new weather_data, do a screen update, clear the screen]
        if self._is_weatherdata_expired() == True:
            response[0] = True
        
        if self._update_times['screen_update'] != self.rtc.datetime()[4]: # Check if its time to update the screen. Updates ~every whole hour.
            response[1] = True
            
        if self._update_times['screen_cleaned'] == False and 2 == self.rtc.datetime()[4]: # If its 2 at night UTC, do the daily clearing of screen.
            response[2] = True
            
        elif self._update_times['screen_cleaned'] == True and 2 != self.rtc.datetime()[4]: # If screen cleaned bool is true and the time is not 2am.
            self._update_times['screen_cleaned'] = False # Set the value back to false.
            
        return response
    
    def set_screen_updated(self):
        """
        Mark the screen as updated.
        Should be run when the screen is done drawing.
        This ensures it only draws after ~1 hour.
        """
        self._update_times['screen_update'] = self.rtc.datetime()[4]
        
    def set_screen_cleaned(self):
        """
        Mark the screen as cleaned.
        """
        self._update_times['screen_cleaned'] = True
