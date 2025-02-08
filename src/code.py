# UPDATE the settings.toml file before starting!

# Following are imported from circuitpython 9.x
import gc
import os
import displayio
import time
import framebufferio
from rgbmatrix import RGBMatrix 
import board
#print(dir(board))
 
RGB_PINS = [board.GP2, board.GP3, board.GP4, board.GP5, board.GP8, board.GP9]
ADDR_PINS = [board.GP10, board.GP16, board.GP18, board.GP20]
CLOCK_PIN = board.GP11
LATCH_PIN = board.GP12
OUTPUT_ENABLE_PIN = board.GP13

icon_spritesheet_file = "/images/weather-icons.bmp"
splash_img_file = "/images/ws.bmp"
time_format_flag = 0 # 12 or 24 (0 or 1) hour display.

BASE_WIDTH = 64
BASE_HEIGHT = 32

## Set this to be either 32 or 64 based on the size matrix you have.
BIT_DEPTH_VALUE = 1
CHAIN_ACROSS = 1
TILE_DOWN = 1
SERPENTINE_VALUE = True

from version import Version
version = Version()
# read the version if it exists.
print(f'Version: {version.get_version_string()}')

# release displays  before creating a new one.
displayio.release_displays()

calcuated_width = BASE_WIDTH * CHAIN_ACROSS
calculated_height = BASE_HEIGHT * TILE_DOWN

# This next call creates the RGB Matrix object itself. It has the given width
# and height. bit_depth can range from 1 to 6; higher numbers allow more color
# shades to be displayed, but increase memory usage and slow down your Python
# code. If you just want to show primary colors plus black and white, use 1.
# Otherwise, try 3, 4 and 5 to see which effect you like best.

matrix = RGBMatrix(
    width = calcuated_width, 
    height=calculated_height, 
    bit_depth=BIT_DEPTH_VALUE,
    rgb_pins=RGB_PINS,
    addr_pins=ADDR_PINS,
    clock_pin=CLOCK_PIN,
    latch_pin=LATCH_PIN,
    output_enable_pin=OUTPUT_ENABLE_PIN,
    tile=TILE_DOWN,
    serpentine=SERPENTINE_VALUE,
    doublebuffer=True,
)
del calcuated_width, calculated_height

# project classes 
from splash_display import SplashDisplay
# Associate the RGB matrix with a Display so that we can use displayio features
display = framebufferio.FramebufferDisplay(matrix, auto_refresh=True)

splash = SplashDisplay(splash_img_file, version)
display.root_group = splash
print('free memory', gc.mem_free(), gc.mem_alloc())

from settings_display import SETTINGS, SettingsDisplay
from date_utils import DateTimeProcessing
from key_processing import KeyProcessing
from light_sensor import LightSensor
from network import WifiNetwork
from weather.tempest_weather import TempestWeather
from weather.weather_display import WeatherDisplay
from persistent_settings import Settings
from buzzer import Buzzer



try:
    network = WifiNetwork() # TODO: catch exception and do something meaninful with it.
except Exception as e:
    print('Network exception?', e)
    # TODO: Display wifi config icon 
    
icons = displayio.OnDiskBitmap(open(icon_spritesheet_file, "rb"))

settings = Settings()
buzzer = Buzzer(settings)
light_sensor = LightSensor(settings)

datetime = DateTimeProcessing(settings, network)
key_input = KeyProcessing(settings, datetime, buzzer)

weather_display = WeatherDisplay(display, icons)

try:
    weather = TempestWeather(weather_display, network, datetime)
except Exception as e:
    print(f"Unable to configure weather, exiting: {e}")
    try:
        from error_display import ErrorDisplay
        print('error_display')
        error_display = ErrorDisplay("/images/config_error.bmp", str(e))
        print('display')
        display.root_group = error_display
        while True:
            error_display.scroll()
        # Pause here and stop processing.
    except Exception as ex:
        print(ex)
    # if error display errored out then exit.
    import sys
    sys.exit()


#Update the clock when first starting.
# TODO: Make async
datetime.update_from_ntp()
last_ntp = time.time()

# Get the initial display and set it.
weather.show_weather()
last_weather = time.time()
settings_visited = False

# remove splash from memory
#del bg, splash
del version, splash
gc.collect()

print('free memory', gc.mem_free())
while True:
    # Always process keys first
    key_value = key_input.get_key_value()
    key_input.key_processing(key_value)

    if key_value is None and key_input.page_id == 0: # normal display
        if settings_visited:
            settings_visited = False
            del settings_display
            while len(weather_display.scroll_queue) > 0:
                weather_display.scroll_queue.popleft()
            weather.show_weather()
            gc.collect()
            
        # current_time in seconds > start_time in seconds + interval in seconds.
        if time.time() > last_ntp + datetime.get_interval():
            datetime.update_from_ntp()
            last_ntp = time.time()
        if weather.show_datetime(): # returns true if autodim enabled and outside of time
            darkmode = light_sensor.get_display_mode()
            weather_display.set_display_mode(darkmode)
            #This is a hack to try to stop buzzer from buzzing while doing something that might hang.
            if not buzzer.is_beeping():
                if weather.weather_complete() and time.time() > last_weather + weather.get_update_interval():
                    weather.show_weather()
                    last_weather = time.time()
                weather_display.scroll_label(key_input)

    elif key_input.page_id == 1: # Process settings pages
        if not settings_visited:
            weather.display_off()
            settings_visited = True
        settings_display = SettingsDisplay(display, datetime)
        settings_display.showSetListPage(key_input.select_setting_options)
        
    elif key_input.page_id == 2: # Process settings pages
        if SETTINGS[key_input.select_setting_options]["type"] == 'set_time':
            settings_display.timeSettingPage(key_input.select_setting_options, key_input.time_setting_label)
        elif SETTINGS[key_input.select_setting_options]["type"] == 'set_date':
            settings_display.dateSettingPage(key_input.select_setting_options, key_input.time_setting_label)
        elif SETTINGS[key_input.select_setting_options]["type"] == 'bool':
            settings_display.onOffPage(
                key_input.select_setting_options, 
                settings
            )
        elif SETTINGS[key_input.select_setting_options]["type"] == 'number':
            settings_display.number_display_page(key_input.select_setting_options, settings)
        elif SETTINGS[key_input.select_setting_options]["type"] == 'time':
            settings_display.time_page(
                key_input.select_setting_options,
                SETTINGS[key_input.select_setting_options]["text"],
                settings.on_time if key_input.select_setting_options == 8 else settings.off_time
            )