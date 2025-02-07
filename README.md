# MicroPython ePaper Weather Station

This project is a weather station built using MicroPython on a Raspberry Pi Pico W and a Waveshare 5.65-inch ePaper display. It fetches and displays weather data for a specified location.

## Screenshot
The device shows the weather data for Now, +4 hours, +8 hours, and tomorrow at 12:00. The small images are loaded from flash, the big image is fetched from my personal API. The reason the big images are in the API is because there is not enough storage on the flash. Feel free to use the api as is if you dont want to host your own.
<p align="left">
  <img src="https://github.com/frederik-andersen/micropython-ePaperWeatherStation/blob/main/screenshots/IMG_0831.jpeg" width="600">
</p>

## Features
- **Weather Data**: Retrieves weather data from the MET Weather API.
- **ePaper Display**: Utilizes a Waveshare 5.65-inch ePaper display to display weather updates.
- **Wi-Fi Connectivity**: Connects to Wi-Fi to fetch the latest weather information.
- **Real-Time Updates**: Updates weather data and display in real-time.
- **Customizable Location**: Easily set your location to get accurate weather data.

## Components
- **MicroPython**: The project is written in MicroPython.
- **Raspberry Pi Pico 2 W**: The microcontroller used for this project.
- **Waveshare 5.65-inch ePaper Display**: The display used to show weather data.

## Getting Started
### Prerequisites
- Raspberry Pi Pico 2 W
- Waveshare 5.65-inch ePaper display
- MicroPython firmware installed on the Pico W
- Wi-Fi network

### Installation
1. **Clone the Repository**:  
   ```sh
   git clone https://github.com/frederik-andersen/micropython-ePaperWeatherStation.git
    ```
2. **Set Up Wi-Fi Credentials**:  
Open datafetcher.py and replace the placeholders with your actual Wi-Fi SSID and password:
    ```
    _SSID = "WIFI_SSID_PLACEHOLDER"
    _WIFI_TOKEN = "WIFI_PASSWORD_PLACEHOLDER"
    ```
3. **Change header for MET API**:  
Open datafetcher.py and replace the placeholder with your email. This is required by MET API.
    ```
    self.USER_AGENT_HEADER = {'User-Agent': 'pico-ePaper-weather-station v.1.0.0 PLACEHOLDER@PLACEHOLDER.com'}
    ```
4. **Add your location**:  
   - Default location is "drammen".
   - Go get the latitude, longitude and altitude for the place you want weather data.
   - Add your location to the locations dictionary in DataFetcher.
     ```python
     self.locations = {
         'drammen': {'latitude': 59.7396, 'longitude': 10.2046, 'altitude': 3},
         'oslo': {'latitude': 59.9108, 'longitude': 10.7577, 'altitude': 4}
     }
     ```
5. **Input correct location in main.py**:  
In main.py input the new location to DataFetcher.
    ```python
    data = DataFetcher('drammen')
    ```

6. **Optional: Translate to your language**:  
   The code is in English, but in ScreenManager the text is in Norwegian.
   Text to be translated:
  -  "Nå" -> "Now"
  -  "i morgen" -> "tomorrow"
  -  "Sist oppdatert" -> "Last update"
   
7. **Optional: Run your own api**:  
  - The code uses my API to store large images.
  - If you want other images than mine, you should run your own API. See the flask_api folder and run it on pythonanywhere.com.

8. **Upload the Code to Pico W**:
  - Use a tool like Thonny or rshell to upload the code to your Raspberry Pi Pico 2 W.
  - Do not upload the screenshots and flask_api directories.


### Usage
1. **Power On the Pico W**:
   - Connect your Raspberry Pi Pico W to a power source.

2. **View Weather Data**:
   - The ePaper display will show the current weather data for your specified location. The data is updated every hour, and the screen is cleared once every 24 hours at 02:00 UTC to prevent ghosting.

## TODO:
- Handling wintertime and summertime. Wintertime is now hardcoded in TimeManager.


## Modifications and new libraries:
- The ePaper [driver](https://github.com/frederik-andersen/micropython-ePaper-5in65-border-color "New epaper driver") is changed so border color can be changed, and the buffer is allocated outside the class. This is to prevent memory leaks that happend with the original driver.

- EasyWriter is a library written by me to make it easier to add text and binary images to the screen.

- [Image to byte array](https://github.com/frederik-andersen/python-image_to_bytearray "Image to byte array") is used to convert ditered png files to binaries.
- [New epaper driver](https://github.com/frederik-andersen/micropython-ePaper-5in65-border-color "New epaper driver") is used to set the border color

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements
- [**Peter Hinch**](https://github.com/peterhinch "PeterHinch"): For the writer class used for text rendering.
- [**Waveshare**](https://github.com/waveshareteam/e-Paper "Waveshare"): For the ePaper display and driver.
- [**MET Weather API**](https://api.met.no/weatherapi/locationforecast/2.0/documentation "MET Weather API"): The weather api used for all data.
- [**MET Weather API icons**](https://github.com/metno/weathericons "MET Weather API icons"): For the weather images.
- [**Pythonanywhere**](https://www.pythonanywhere.com/ "Pythonanywhere"): For free python flask hosting.
