# EasyWriter by Frederik Andersen
# Version 1.0.0
# Library to make it easy to get text and images on ePaper display.
# Only tested on Waveshare Pico-ePaper-5.65 7-color.
# Text is in black and white, pictures can be color.
# Released under the MIT License (MIT). See LICENSE.
#
# Uses Peter Hinch writer class for text.
# Released under the MIT License (MIT).
# https://github.com/peterhinch/micropython-font-to-py/tree/master/writer

import framebuf
from writer import Writer

# Screen size in pixels
EPD_WIDTH = 600 # Screen width
EPD_HEIGHT = 448 # Screen height

class EasyWriter():
    def __init__(self, device, font, verbose=True):
        self.device = device
        self.writer = Writer(device, font, verbose=True)

    def change_font(self, font):
        """
        Method to change font/font-size.
        Must be used before add_text method.
        """
        self.writer.font = font
        
    def add_text(self, line, width_pos, height_pos):
        """
        Write the text at desired x and y position.
        line: 		string = the string to be written.
        height_pos: int = position the text gonna be in the height pane of the screen.
        width_pos: 	int = position the text gonna be in the width pane of the screen.
        """
        self.writer.set_textpos(self.device, height_pos, width_pos)
        self.writer.printstring(line, invert=True)
        
    def add_text_center(self, line, width_start_pos=0, width_end_pos=EPD_WIDTH, height_start_pos=0, height_end_pos=EPD_HEIGHT):
        """
        Method to center text horizontally at the desired height.
        line: 				string = the string to be written.
        height_pos:     	int = position the text gonna be in the height pane of the screen.
        width_start_pos: 	int = start position of the screen where text should be centered.
        width_end_pos: 		int = end position of the screen where text should be centered.
        height_start_pos: 	int = start position of the screen where text should be centered.
        height_end_pos: 	int = end position of the screen where text should be centered.
        """
        
        font_height = self.writer.font.height()
        workspace_height = height_end_pos - height_start_pos # The height of the area the text should be centered.
        height_pos = height_start_pos + ((workspace_height - font_height) // 2) # Get the position for the text. 
        
        length = self.writer.stringlen(line)
        workspace_width = width_end_pos - width_start_pos # The width of the area the text should be centered.
        width_pos = width_start_pos + ((workspace_width - length) // 2) # Get the position for the text. 

        self.add_text(line, height_pos, width_pos)

    def add_text_horizontal_center(self, line, height_pos, width_start_pos=0, width_end_pos=EPD_WIDTH):
        """
        Method to center text horizontally at the desired height.
        line: 				string = string to be written.
        height_pos: 		int = position the text gonna be in the height pane of the screen.
        width_start_pos: 	int = start position of the screen where text should be centered.
        width_end_pos: 		int = end position of the screen where text should be centered.
        """
        length = self.writer.stringlen(line)
        workspace_width = width_end_pos - width_start_pos # The width of the area the text should be centered.
        width_pos = width_start_pos + ((workspace_width - length) // 2) # Get the position for the text. 
        
        self.add_text(line, width_pos, height_pos)
    
    def add_text_vertical_center(self, line, width_pos, height_start_pos=0, height_end_pos=EPD_HEIGHT):
        """
        Method to center text vertically at the desired height.
        line: 				string = string to be written.
        width_pos: 			int = position the text gonna be in the width pane of the screen.
        height_start_pos: 	int = start position of the screen where text should be centered.
        height_end_pos: 	int = end position of the screen where text should be centered.
        """
        font_height = self.writer.font.height()
        workspace_height = height_end_pos - height_start_pos # The height of the area the text should be centered.
        height_pos = height_start_pos + ((workspace_height - font_height) // 2) # Get the position for the text. 
        
        self.add_text(line, width_pos, height_pos)
        
    def add_image(self, image, img_width=EPD_WIDTH, img_height=EPD_HEIGHT, width_pos=0, height_pos=0):
        """
        Method for adding 7-color image in byte array format to the screen.
        image: 		bytes = image to be written to screen.
        img_width: 	int = image width in pixels.
        img_height: int = image height in pixels.
        """
        for y in range(img_height):
            for x in range(img_width):
                if y + height_pos < self.device.height and x + width_pos < self.device.width:
                    color = image[y * img_width + x]
                    self.device.pixel(x + width_pos, y + height_pos, color)
    
    def add_image_center(self, image, img_width, img_height, width_start_pos=0, width_end_pos=EPD_WIDTH, height_start_pos=0, height_end_pos=EPD_HEIGHT):
        """
        Method to center image horizontally, at the desired height position.
        image: 				bytes = image to be written to screen.
        img_width: 			int = image width in pixels.
        img_height: 		int = image height in pixels.
        width_start_pos: 	int = start position
        width_end_pos: 		int = end position
        height_start_pos: 	int = start position
        height_end_pos: 	int = end position
        """
        workspace_width = width_end_pos - width_start_pos # The width of the area the text should be centered.
        workspace_height = height_end_pos - height_start_pos # The height of the area the image should be centered.
        
        width_pos = width_start_pos + ((workspace_width - img_width) // 2) # Get the position for the image.
        height_pos = height_start_pos + ((workspace_height - img_height) // 2) # Get the position for the image.
        
        self.add_image(image, img_width, img_height, width_pos, height_pos)
    
    def add_image_horizontal_center(self, image, img_width, img_height, height_pos, width_start_pos=0, width_end_pos=EPD_WIDTH):
        """
        Method to center image horizontally at the desired height position.
        image: 				bytes = image to be written to screen.
        img_width: 			int = image width in pixels.
        img_height: 		int = image height in pixels.
        height_pos: 		int = position the image gonna be in the height pane of the screen.
        width_start_pos: 	int = start position of the screen where image should be centered.
        width_end_pos: 		int = end position of the screen where image should be centered.
        """
        workspace_width = width_end_pos - width_start_pos # The width of the area the image should be centered.
        width_pos = width_start_pos + ((workspace_width - img_width) // 2) # Get the position for the image.
        self.add_image(image, img_width, img_height, width_pos, height_pos)
    
    def add_image_vertical_center(self, image, img_width, img_height, width_pos, height_start_pos=0, height_end_pos=EPD_HEIGHT):
        """
        Method to center image vertically at the desired width position.
        image: 				bytes = image to be written to screen.
        img_width: 			int = image width in pixels.
        img_height: 		int = image height in pixels.
        width_pos: 			int = position the image gonna be in the width pane of the screen.
        height_start_pos: 	int = start position of the screen where image should be centered.
        height_end_pos: 	int = end position of the screen where image should be centered.
        """
        workspace_height = height_end_pos - height_start_pos # The height of the area the image should be centered.
        height_pos = height_start_pos + ((workspace_height - img_height) // 2) # Get the position for the image.
        self.add_image(image, img_width, img_height, width_pos, height_pos)
            
    def refresh(self):
        """
        Method spesific for EPD_5IN65F, do not use if you dont use that device.
        Refreshes the screen with the data in buffer.
        """
        self.device.EPD_5IN65F_Display(self.device.buffer)
        
    def sleep(self):
        """
        Method spesific for EPD_5IN65F, do not use if you dont use that device.
        Call sleep method on the device.
        """
        self.device.Sleep()
        
