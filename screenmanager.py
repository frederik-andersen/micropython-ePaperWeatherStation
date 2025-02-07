# ScreenManager by Frederik Andersen
# Class to manage the ePaper/eInk screen.
# Released under the MIT License (MIT). See LICENSE for details.

import gc
import utime
import machine
from lib.e_ink_lib import EPD_5in65
from lib.easywriter import EasyWriter
from errorhandler import ErrorHandler
import fonts.opensans80, fonts.opensans32, fonts.opensans16



class ScreenManager():
    
    def __init__(self, data_fetcher, time_manager):
        """
        Initializes the ScreenManager with a DataFetcher and TimeManager.

        Parameters:
        data_fetcher (DataFetcher): An instance of the DataFetcher class.
        time_manager (TimeManager): An instance of the TimeManager class.
        """
        self.data_fetcher = data_fetcher
        self.time_manager = time_manager
        self.screen_buffer = bytearray(600 * 448 // 2) # buffer for the display, get memory leaks if not global outside the driver.
    
    def clear(self):
        """
        Clears the screen.

        The screen should be cleared every 24 hours. 
        If you plan to store the device, run this method to clear the screen for storage.
        """
        gc.collect()
        epd = EPD_5in65(self.screen_buffer)  # The screen
        epd.EPD_5IN65F_Clear(epd.White)
        epd.Sleep()
        self.time_manager.set_screen_cleaned()
        
    def draw(self):
        """
        Updates and draws the screen with all its content.
        
        This method initializes the screen, draws weather data, date, and lines, 
        then refreshes and puts the screen to sleep to prevent damage.
        """
        ew = self._init_screen()
        ew.device.fill(ew.device.White) # White background.
        
        self._draw_weather_data(ew)
        self._draw_date(ew)
        self._draw_lines(ew)
        
        ew.refresh()
        ew.sleep()  # ALWAYS run this after writing to the screen, may cause physical damage to screen if not.
        
        # Next draw should be in 1 hour. Set that the screen just have been updated.
        self.time_manager.set_screen_updated()
    
    def _init_screen(self):
        """
        Initializes the screen and EasyWriter.

        This method is used to write to the screen multiple times. 
        After the screen goes to sleep, everything needs to be re-initialized.

        Returns:
        EasyWriter: An instance of the EasyWriter class.
        """
        gc.collect()
        try:
            epd = EPD_5in65(self.screen_buffer)  # The screen
            ew = EasyWriter(epd, fonts.opensans16) # EasyWriter for easier use of the writer class
            return ew
        
        except MemoryError:
            print(gc.mem_free())
            print("Soft reset...")
            machine.soft_reset()
            
        
    def _draw_weather_data(self, ew):
        """
        Draws all weather data including text and icons on the display.

        Parameters:
        ew (EasyWriter): An instance of the EasyWriter class used to draw text and images on the display.
        """
        hour_now = self.time_manager.get_datetime()[4]
        hour_plus_4 = self.time_manager.get_time_with_delta(4)
        hour_plus_8 = self.time_manager.get_time_with_delta(8)
        
        # Must be fetched first, or the pico will not have enough ram for the request to the api.
        tomorrow_12h_temp, tomorrow_12h_icon = self.data_fetcher.get_weather_data(day_delta=1, spesific_time=12)
        
        current_temp, current_icon = self.data_fetcher.get_weather_data()  # Get current temperature outside.
        plus_4h_temp, plus_4h_icon = self.data_fetcher.get_weather_data(time_delta=4)  # Get current temperature outside.
        plus_8h_temp, plus_8h_icon = self.data_fetcher.get_weather_data(time_delta=8)  # Get current temperature outside.
        
        
        ew.change_font(fonts.opensans32) # Change font size
        
        # Data now
        ew.add_text_vertical_center("Nå", width_pos=45, height_start_pos=63, height_end_pos=170)
        ew.add_image_vertical_center(image=current_icon, img_width=80, img_height=80, width_pos=100, height_start_pos=63, height_end_pos=170)
        ew.add_text_vertical_center(f"{current_temp}°", width_pos=200, height_start_pos=63, height_end_pos=170)
        
        # Data +4h
        ew.add_text_vertical_center(f"{hour_plus_4}", width_pos=45, height_start_pos=170, height_end_pos=277)
        ew.add_image_vertical_center(image=plus_4h_icon, img_width=80, img_height=80, width_pos=100, height_start_pos=170, height_end_pos=277)
        ew.add_text_vertical_center(f"{plus_4h_temp}°", width_pos=200, height_start_pos=170, height_end_pos=277)
        
        # Data +8h
        ew.add_text_vertical_center(f"{hour_plus_8}", width_pos=45, height_start_pos=277, height_end_pos=374)
        ew.add_image_vertical_center(image=plus_8h_icon, img_width=80, img_height=80, width_pos=100, height_start_pos=277, height_end_pos=374)
        ew.add_text_vertical_center(f"{plus_8h_temp}°", width_pos=200, height_start_pos=277, height_end_pos=374)
        
        # Tomorrow at 12:00
        ew.add_image_horizontal_center(image=tomorrow_12h_icon, img_width=200, img_height=200, height_pos=50, width_start_pos=300, width_end_pos=600)
        ew.add_text_horizontal_center(f"{tomorrow_12h_temp}°", height_pos=260, width_start_pos=300, width_end_pos=600)
        ew.add_text_horizontal_center("i morgen", height_pos=300, width_start_pos=300, width_end_pos=600)

        
        print("Free memory after allocating all content to buffer:", gc.mem_free())

    
    def _draw_date(self, ew):
        """
        Draw date and line under on top of the screen.
        Draw date and time the screen was last updated.
        """
        date_and_time = self.time_manager.get_datetime() # Weekday, day, month, year, hour, minute
        ew.change_font(fonts.opensans16)
        
        #ew.add_text(f"{date_and_time[0]} {date_and_time[1]}.{date_and_time[2]} {date_and_time[3]}", 10, 10)
        ew.add_text(f"Sist oppdatert: {date_and_time[4]}:{date_and_time[5]}", 440, 417)
        #ew.add_text(f"Sist oppdatert: {date_and_time[4]}:{date_and_time[5]}", 10, 417)
        
    def _draw_lines(self, ew):
        """
        Draw all lines on screen.
        """
        #ew.device.hline(0, 33, 600, ew.device.Black) # Pos x, Pos Y, lenght, color
        ew.device.hline(60, 170, 180, ew.device.Black) # Pos x, Pos Y, lenght, color
        ew.device.hline(60, 277, 180, ew.device.Black) # Pos x, Pos Y, lenght, color
        ew.device.vline(300, 60, 330, ew.device.Black) # Pos x, Pos Y, lenght, color
    
