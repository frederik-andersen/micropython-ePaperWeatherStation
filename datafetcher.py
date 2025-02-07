# DataFetcher by Frederik Andersen
# Class to handle all data from the MET Weather API and my personal API.
# The MET Weather API requires a unique user agent to use their API, and your email should be included.
# This is stated under the terms of service for the API: https://api.met.no/doc/TermsOfService
# Released under the MIT License (MIT). See LICENSE for details.

import gc
import os
import json
import utime
import network
import lib.mrequests as requests
from machine import RTC
from errorhandler import ErrorHandler

class DataFetcher():
    
    _SSID = "WIFI_SSID_PLACEHOLDER"
    _WIFI_TOKEN = "WIFI_PASSWORD_PLACEHOLDER"
    
    def __init__(self, location):
        """
        Initializes the DataFetcher with a specified location.

        Parameters:
        location (str): The name of the location to fetch data for.
        """
        self.USER_AGENT_HEADER = {'User-Agent': 'pico-ePaper-weather-station v.1.0.0 PLACEHOLDER@PLACEHOLDER.com'} # This header must be changed to your email.
        self.location = location
        self.locations = {'drammen': {'latitude': 59.7396, 'longitude': 10.2046, 'altitude': 3},
                          'oslo': {'latitude': 59.9108, 'longitude': 10.7577, 'altitude': 4}
                          }
        self._is_wifi_enabled()
        
    def _is_wifi_enabled(self):
        """
        Checks if Wi-Fi is enabled and connects if not.
        Ensures Wi-Fi is enabled. If not, attempts to enable it. If connection fails, retries after a delay.
        """
        wlan = network.WLAN(network.STA_IF)
        if wlan.isconnected() == False: # If not connected to wifi.
            print("Not connected to wifi...")
            try:
                self._enable_wifi(wlan) # Connect to wifi.
            except Exception as e:
                ErrorHandler(e)
                
                while True:
                    ErrorHandler.retry_timer() # Flashes led and waits 5 minutes before continuing this loop.
                    try:
                        self._enable_wifi(wlan) # Connect to wifi
                    except:
                        continue
            
    def _enable_wifi(self, wlan):
        """
        Connects to Wi-Fi.

        Parameters:
        wlan (network.WLAN): The WLAN object to use for the connection.
        
        Raises:
        RuntimeError: If the network connection fails.
        """
        # Activate wlan.
        wlan.active(True) 

        # Connect to your network
        wlan.connect(self._SSID, self._WIFI_TOKEN)

        # Wait for Wi-Fi connection
        connection_timeout = 30
        while connection_timeout > 0:
            if wlan.status() >= 3:
                break
            connection_timeout -= 1
            print('Waiting for Wi-Fi connection...')
            utime.sleep(1)

        # Check if connection is successful
        if wlan.status() != 3:
            raise RuntimeError('Failed to establish a network connection.')
        else:
            print('Connection successful!')
            network_info = wlan.ifconfig()
            print('IP address:', network_info[0])
    
    def _read_file(self, filename, bypass_error=False):
        """
        Read and return data.
        returns data if read is successful else raise exception.
        
        Parameters:
        filename (str): filename without extention.
        bypass_error (bool): used to bypass the error drawing to the screen. Normally False.
        """
        """
        Reads and returns data from a JSON file.

        Parameters:
        filename (str): The name of the file (without extension) to read.
        bypass_error (bool): If True, bypasses error handling. Default is False.

        Returns:
        dict or list: The data read from the file.

        Raises:
        OSError: If there is an error reading the file.
        """
        try:
            with open(f'data/{filename}.json', 'r') as file:
                data = json.load(file)
                return data
            
        except OSError as e:
            if bypass_error == False:
                exception_string = f"Error trying to open file: OSError {e}"
                ErrorHandler(exception_string)
            raise
    
    def _save_file(self, filename, data):
        """
        Saves data to a JSON file.

        Parameters:
        filename (str): The name of the file (without extension) to save.
        data (dict): The data to save.
        """
        with open(f'data/{filename}.json', 'w') as file:
                json.dump(data, file)
        os.sync() # Make sure the filesystem is up to date after the new file is added.
    
    def get_image(self, image_name):
        """
        Retrieves a binary image from flash storage.

        Parameters:
        image_name (str): The name of the image file (without extension).

        Returns:
        bytes: The binary data of the image.

        Raises:
        Exception: If there is an error loading the image.
        """
        try:
            with open(f'images/{image_name}.bin', 'rb') as file:
                image = file.read()
                return image
                
        except Exception as e:
            exception_string = f"Error loading image: {e}"
            ErrorHandler(exception_string)
            raise
        
    def fetch_new_weather_data(self):
        """
        Fetches weather data from the MET Weather API for the specified location.

        Saves the fetched data and headers to JSON files.

        Raises:
        Exception: If there is an error connecting to the MET Weather API.
        """
        lat = self.locations[self.location.lower()]['latitude']
        lon = self.locations[self.location.lower()]['longitude']
        alt = self.locations[self.location.lower()]['altitude']
        
        self._is_wifi_enabled() # Ensure that wifi is connected.
    
        # GET weather data from MET using mini.json.
        # Can use compact or complete parameter instead of mini.json if more data is needed.
        weather_data = requests.get(
            f'https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={lat}&lon={lon}&altitude={alt}', headers=self.USER_AGENT_HEADER, save_headers=True)
        
        if weather_data.status_code != 200:  # 200 = successful connection to MET API, anything else is an error.
            exception_string = f"MET Weather API connection error: {weather_data.status_code}"
            ErrorHandler(exception_string)
            raise Exception(exception_string)
        else:
            self._save_file(f'{self.location}', weather_data.json()) # Save the data from the api
            self._save_file(f'{self.location}_headers', weather_data.headers) # Save the header.

            #self._data_expire_time = weather_data.headers['Expires']

            weather_data.close()
            gc.collect()
            
    def _get_weather_icon(self, icon_requested):
        """
        Fetches a weather icon from a Frederik API.
        All the weather icons takes up to much space to save it to the flash.
        The solution was to put it on a flask api using pythonanywhere.com.

        Parameters:
        icon_requested (str): The name of the requested weather icon (without extension).

        Returns:
        bytes: The binary data of the weather icon.

        Raises:
        Exception: If there is an error connecting to the Frederik API.
        """
        self._is_wifi_enabled() # Ensure that wifi is connected.
        gc.collect()
        icon_recieved = requests.get(
                f'https://frederikapi.pythonanywhere.com/api/?requested-icon={icon_requested}', headers=self.USER_AGENT_HEADER)
        
        if icon_recieved.status_code != 200:  # 200 = successful connection to frederikapi, anything else is an error.
                exception_string = f"Frederik API connection error: {icon_recieved.status_code}, Requested icon: {icon_requested}"
                ErrorHandler(exception_string)
                print(icon_recieved.headers)
                raise Exception(exception_string)

        else:
            data = icon_recieved.content
            icon_recieved.close()
            gc.collect()
            return data
        
        
    def get_weather_data(self, time_delta=0, day_delta=0, spesific_time=None):
        """
        Retrieves the temperature and associated weather icon.

        Parameters:
        time_delta (int): The number of hours to add to the current time to get the requested hour.
        day_delta (int): The number of days to add to the current day to get the requested day.
        specific_time (int): The hour requested. Used if day_delta is specified.
        
        Returns:
        tuple:
            int: The temperature.
            bytes: The weather icon as binary data.
        """
        clock = RTC()
        current_time = clock.datetime()
        
        if day_delta == 0: # If no day delta is specified.
            requested_hour = current_time[4] + time_delta
            
            if requested_hour >= 24:
                requested_hour -= 24
            
        else: # If wanted current day + x days and spesific time.
            current_time_tuple = current_time[:7] + (0,) # Ensure the tuple has the correct length
            current_time_seconds = utime.mktime(current_time_tuple) # Convert to seconds since epoch
            next_time_seconds = current_time_seconds + (day_delta * 86400) # Add one day (86400 seconds)
            next_datetime = utime.localtime(next_time_seconds) # Convert back to datetime
            
            next_date = next_datetime[:3] # Extract the date part (year, month, day)
            
            requested_hour = spesific_time # The hour as int
            requested_date = (next_date[1], next_date[2]) # (month, day)
        
        weather_data = self._read_file(self.location) # Read the weather data.
        
        for data in weather_data['properties']['timeseries']: # Loop trough the data and find correct time.
            time_and_date = data['time'].split("T")
            time = time_and_date[1].split(":") # hour, minute, second
            
            if day_delta == 0:
                if requested_hour == int(time[0]): # If both hours match.
                    temperature = data['data']['instant']['details']['air_temperature'] # Get the current temperature.
                    # weather_icon = self._get_weather_icon(data['data']['next_1_hours']['summary']['symbol_code']) # Get the current weather icon from api.
                    weather_icon = self.get_image(f"{data['data']['next_1_hours']['summary']['symbol_code']}_80x80") # Get 80x80 icon from flash.
                    break
                
            else: # If there is a day delta
                date_list = time_and_date[0].split("-") # Split the date
                month = int(date_list[1]) # Get month
                day = int(date_list[2]) # Get day
                
                #print(f"Requested day: {requested_date[1]}, Requested month: {requested_date[0]}, Requested time{}")
                
                if requested_date[0] == month and requested_date[1] == day and requested_hour == int(time[0]): # If month, day and hour match
                    temperature = data['data']['instant']['details']['air_temperature'] # Get the current temperature.
                    weather_icon = self._get_weather_icon(data['data']['next_1_hours']['summary']['symbol_code']) # Get the 200x200 weather icon from api.
                    break
                    
        return temperature, weather_icon
    
    def get_expiretime_weatherdata(self):
        """
        Retrieves the expiration time for the weather data.

        Returns:
        str: The expiration time as a string.
        """

        try:
            headers_list = self._read_file(f"{self.location}_headers", bypass_error=True) # Bypass error drawing to screen if the file doesnt exist.
            headers_dict = dict(header.split(": ", 1) for header in headers_list)
            
            expire_time = headers_dict['Expires']
            return expire_time
        
        except Exception as e: # The file is not made yet, use fictional http date and time.
            print(e)
            return 'Tue, 14 Jan 2025 12:58:38 GMT'

    