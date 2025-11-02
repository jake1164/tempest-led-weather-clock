# tempest-led-weather-clock
LED Matrix Clock with weather running on a Raspberry Pico 2 W with a WaveShare [Pico-RGB-Matrix-P3-64x32](https://www.waveshare.com/wiki/Pico-RGB-Matrix-P3-64x32) and displaying weather information from a WeatherFlow Tempest weather station. For those without a Tempest check out the Open Weather Maps driven solution [Pico-RGB-Matrix-Weather-Clock](https://github.com/jake1164/Pico-RGB-Matrix-Weather-Clock)

## NOTE: RASPBERRY PICO 2 W is REQUIRED for this to work.
The pico while wonderful has too many memory limitations. The [pico 2 W](https://www.raspberrypi.com/products/raspberry-pi-pico-2/) is a drop in replacement and will make everything just work. 

## NOTE: THIS PROJECT REQUIRES CircuitPython 9.0.0 or later
This project requires that you use [circuitpython 9.x.x](https://circuitpython.org/board/raspberry_pi_pico_w/). 

### [Tempest](https://tempestwx.com/)
Sign into your tempest portal to create a application token under [Settings](https://tempestwx.com/settings) and find your stationID (in the URL after you sign up).
Put the token from [Data Authorizations](https://tempestwx.com/settings/tokens) in the settings.toml file under TEMPEST_API_TOKEN="" and enter the station under the TEMPEST_STATION=xxxxx  where xxxxx is the number from tempestwx.com/station/xxxxx/

## Configuration File Settings
Rename settings.toml.default file to settings.toml on the Pico and adjust the following settings:

### Wifi Settings
* WIFI_SSID="your ssid"
* WIFI_PASSWORD="yoursupersecretpassword"
* NTP_HOST="0.adafruit.pool.ntp.org"
* TZ_OFFSET=<timezone offset> ie TZ_OFFSET=-5
* NTP_INTERVAL=21600  # note: 21600 = 6hr, 43200 = 12hr, 86400 = 24hr
### tempestwx.com (tempest) Data Authorization
* TEMPEST_API_TOKEN="yourDataAuthorizationToken"
* TEMPEST_STATION=0 #YourStationNumber
### Data configuration
* UNITS="imperial" # Valid Settings:  imperial (temp=f, wind=mph, pressure=inhg, precip=in, distance=mi) or metric (temp=c, wind=kph, pressure=mb, precip=cm, distance=km)
### Fine Tuning of settings. Use these settings to adjust any (or all) of the settings
## Temperature (Note this will override the default UNITS setting if enabled)
UNITS_TEMP = "f" # Valid Settings: f or c

## Wind Speed (Note this will override the default UNITS setting if enabled)
UNITS_WIND = "mph" # Valid Settings: mph, kph, kts, mps, bft, lfm

## Pressure units (Note this will override the default UNITS setting if enabled)
UNITS_PRESSURE = "mb" # Valid Settings: mb, inhg, mmhg, hpa

## Amount of rain (Note this will override the default UNITS setting if enabled)
UNITS_PRECIP = "in" # Valid Settings: mm, cm, in

## Lightning strike distance (Note this will override the default UNITS setting if enabled)
UNITS_DISTANCE = "mi" # Valid Settings: km, mi


## Persistant Settings
To enable in application settings you must rename the _boot.py file to boot.py and place it on your device.  

With this setting enabled any changes to the in menu setting ( Buzzer/ Autodim / 12/24 hr clock / Net Time / DST Adjust ) will persist when you turn the device off and turn it back on again. 

Settings:
* NET TIME - Enables automatic time synchronization from Network Time Protocol (NTP) server. When enabled, time is automatically fetched from the internet based on your timezone offset. **Note: NET TIME does not automatically handle Daylight Saving Time - you must manually toggle APPLY DST.**
* APPLY DST - Adds 1 hour for Daylight Saving Time. When NET TIME is enabled, this adjusts the NTP time by +1 hour. When NET TIME is disabled, this manually adjusts the clock by +1 hour. You must manually turn this on/off when entering or leaving DST.
* BEEP SET - Turns the beeping for button presses on and off 
* AUTODIM - When the light sensor detects its dark it will dim the display (turn the LED display off). 
* 12/24 HR - Changes the clock between 12 and 24 hour display.

**NOTE** When boot.py is enabled the drive becomes read only for your computer, to make changes you must hold down the menu / KEY0 button (Bottom button) when you turn on the device. This setting is only read at boot and restarting will have no effect on this setting. 

## Board
This project requires the use of a Raspberry [pico 2 W](https://www.raspberrypi.com/products/raspberry-pi-pico-2/) to use the WIFI for getting information for displaying on the screen such as updated time, and eventually local weather. (api to be defined soon)

## Circuitpython 9.0.0
This project requires that you use [circuitpython 9.x.x](https://circuitpython.org/board/raspberry_pi_pico_w/). 

## Libraries
Circuit libraries are included in the ./lib/src folder, just copy the ./src folder to the Pico. Most of the libraries are located on the 
 CircuitPython [libraries](https://circuitpython.org/libraries) page. 
 Notes: 
 * The schedule library is located in the version 8.x Community Bundle. 
 * The IR_RX library is located on [github](https://github.com/peterhinch/micropython_ir).

## Clock
Connects to a Network Time Protocol server (0.adafruit.pool.ntp.org) and sets the onboard DS3231 RTC based on the time from the NTP response.

## Weather Plugin
Not implemented yetS

## Images
![figure 1](/images/img1.jpg)
![figure 2](/images/img2.jpg)
![figure 3](/images/img3.jpg)
![figure 4](/images/img4.jpg)

# Code Standards
This project moving forward will be converting changed code to loosely meet the
google python [coding standard](https://google.github.io/styleguide/pyguide.html#316-naming). 

## pylint settings
To ignore the code.py overriding the std lib error add the following
to your .vscode.json config file.
```
  "python.languageServer": "Pylance",
  [...]
  "python.analysis.diagnosticSeverityOverrides": {
      "reportShadowedImports": "none"
  },
```

# KNOWN ISSUES
Memory is on the ragged edge of the Pico W limits and as such many api requests fail do to memory allocation issues.
