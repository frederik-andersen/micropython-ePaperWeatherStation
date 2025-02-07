# ErrorHandler by Frederik Andersen
# Class to handle all error messages from the program.
# Released under the MIT License (MIT). See LICENSE for details.

import utime
import machine

class ErrorHandler():
    
    def __init__(self, error_message):
        print(error_message)
        # Used to have more functionallity, but eats up to much ram.
        
    @staticmethod
    def retry_timer():
        """
        Flashes led and returns after 5 minutes.
        """
        counter = 0
        while True:
            ErrorHandler.flash_led()
            counter += 1
            
            if counter >= 150: # After 5 min
                break
        
    @staticmethod
    def flash_led():
        """
        Static method for flashing the onboard led one cycle.
        """
        led = machine.Pin("LED", machine.Pin.OUT)
        led.on()
        utime.sleep(1)
        led.off()
        utime.sleep(1)
    
    @staticmethod
    def turn_on_led():
        """
        Static method for flashing the onboard led one cycle.
        """
        led = machine.Pin("LED", machine.Pin.OUT)
        led.on()
    
    @staticmethod
    def turn_off_led():
        """
        Static method for flashing the onboard led one cycle.
        """
        led = machine.Pin("LED", machine.Pin.OUT)
        led.off()

        