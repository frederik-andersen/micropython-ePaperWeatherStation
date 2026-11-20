# TimeManager by Frederik Andersen
# Class to handle all time-related functionalities.
# Requires an instance of DataFetcher.
# Released under the MIT License (MIT). See LICENSE for details.

import utime
import machine
import random
from ntptime import settime
from errorhandler import ErrorHandler

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
        self._last_sync = None # Time (utime.time) of the last successful NTP sync.
        self._update_times = {'screen_update': None, 'screen_cleaned': False} # Dict for handeling update times.
        for attempt in range(5): # Never continue with a wrong clock. After 5 failed tries the error stops the program.
            try:
                self._set_time()
                break
            except Exception:
                if attempt == 4:
                    raise
                utime.sleep(5)
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
            self._last_sync = utime.time()
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
        now = self.rtc.datetime() # UTC
        year = now[0]
        # Norwegian summertime: from the last Sunday in March 01:00 UTC to the last Sunday in October 01:00 UTC.
        starts = (3, self._last_sunday(year, 3), 1)
        ends = (10, self._last_sunday(year, 10), 1)
        if starts <= (now[1], now[2], now[4]) < ends:
            return self._summertime
        return self._wintertime
    
    def _last_sunday(self, year, month):
        """
        Returns the day of month for the last Sunday. Only for months with 31 days (March and October).
        """
        weekday = utime.localtime(utime.mktime((year, month, 31, 0, 0, 0, 0, 0)))[6] # Monday is 0.
        return 31 - ((weekday + 1) % 7)
    
    def sync_time_if_needed(self):
        """
        Sets the RTC from NTP about once a day, since the RTC drifts.
        Failure is not fatal. It is tried again after one hour.
        """
        if self._last_sync is None or utime.time() - self._last_sync < 86400:
            return
        try:
            self._datafetcher._is_wifi_enabled() # Ensure that wifi is connected.
            self._set_time()
        except Exception:
            self._last_sync = utime.time() - 86400 + 3600 # Try again in one hour.
    
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
            
        rtc_date = self.rtc.datetime() # UTC
        utc_seconds = utime.mktime((rtc_date[0], rtc_date[1], rtc_date[2], rtc_date[4], rtc_date[5], rtc_date[6], 0, 0))
        local = utime.localtime(utc_seconds + time_difference * 3600) # Handles day, month and year changes. Weekday: Monday is 0.
        
        hour = f"{local[3]:02d}" # Always two digits.
        minute = f"{local[4]:02d}"
            
        datetime = [day_converter[local[6]], local[2], month_converter[local[1]], local[0], hour, minute] # Weekday, day, month, year, hour, minute
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
