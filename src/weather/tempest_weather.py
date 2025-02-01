# Pulls weather from a the weatherflow api (from a tempest weather station) 
# https://weatherflow.github.io/Tempest/api/ 
import os

STATIONS_URL = 'https://swd.weatherflow.com/swd/rest/stations?token={}'
BETTER_URL = 'https://swd.weatherflow.com/swd/rest/better_forecast?station_id={}&units_temp=f&units_wind=mph&units_pressure=mmhg&units_precip=in&units_distance=mi&token={}'

# Redo actual icons to be more in line with whats expected.

ICON_MAP = {
    'clear-day': 'CLEAR_DAY',
    'clear-night': 'CLEAR_NIGHT',
    'cloudy': 'CLOUDY',
    'foggy': 'MIST',
    'partly-cloudy-day': 'PARTLY_CLOUDY_DAY',
    'partly-cloudy-night': 'PARTLY_CLOUDY_NIGHT',
    'possibly-rainy-day': 'SHOWER',
    'possibly-rainy-night': 'SHOWER',
    'possibly-sleet-day': 'SNOW',
    'possibly-sleet-night': 'SNOW',
    'possibly-snow-day': 'SNOW',
    'possibly-snow-night': 'SNOW',
    'possibly-thunderstorm-day': 'THUNDERSTORM',
    'possibly-thunderstorm-night': 'THUNDERSTORM',
    'rainy': 'RAIN',
    'sleet': 'SNOW',
    'snow': 'SNOW',
    'thunderstorm': 'THUNDERSTORM',
    'windy': 'MIST'
}

class TempestWeather():
    def __init__(self, weather_display, network, datetime, units) -> None:
        self._units = units
        self._network = network
        self._weather_display = weather_display
        self._datetime = datetime

        token = os.getenv('TEMPEST_API_TOKEN')
        station = os.getenv('TEMPEST_STATION')
        #self._url = URL.format(station, token)
        self._url = BETTER_URL.format(station, token)
        self._missed_weather = 0
        self.skip = 0
        self.pixel_x = 0
        self.pixel_y = 0

    def get_weather(self):
        weather = self._network.getJson(self._url)
        #print(weather)
        # TODO: reduce size of json data and purge gc

        return weather


    def get_update_interval(self):
        """ Returns the weather update interval in seconds """
        return 20

    def show_weather(self):
        try:
            weather = self.get_weather()            
        except Exception as ex:
            print('unable to get weather', ex)
            weather = None

        if weather == {} or weather['current_conditions'] == None or len(weather['current_conditions']) == 0:
            if self._missed_weather > 5: 
                self._weather_display.hide_temperature()
                self._weather_display.add_text_display("Unable to contact API")
            # else if 10 updates then restart the device?
            else:
                self._missed_weather += 1
            
            self._weather_display.show() #TODO: is this required?
            return
        else: 
            self._missed_weather = 0

        try:
            print(weather['current_conditions'])
            if 'icon' in weather['current_conditions'].keys():
                # Map tempest weather icon to the standard weather icon
                icon_name = weather['current_conditions'].get('icon', 'clear-day')
                icon = ICON_MAP.get(icon_name, 'CLEAR_DAY')
                self._weather_display.set_icon(icon)

            self._apply_reading('air_temperature', weather, self._weather_display.set_temperature)
            
            # TODO: Make these generic display methods to add to the QUEUE.  
            # Note we need to be sure to wait for the display to catch up?  or only update the temperature until QUEUE is empty?
            self._apply_reading('relative_humidity', weather, self._weather_display.set_humidity)  
            self._apply_reading('feels_like', weather, self._weather_display.set_feels_like)
            self._apply_reading('wind_avg', weather, self._weather_display.set_wind)
            self._apply_reading('conditions', weather, self._weather_display.set_description)
            
            # TODO: In theory I could assume anything else is a straight read from data
        except Exception as ex:
            print('Unable to display weather', ex)
        finally:
            self._weather_display.show()


    def show_datetime(self) -> bool:
        changed = self._weather_display.set_time(self._datetime.get_time())

        if changed and self._datetime.is_display_on:
            self._weather_display.show()

        if self._datetime.is_display_on:
            self._weather_display.hide_pixel(self.pixel_x, self.pixel_y)
        else:
            # Get current pixel being shown
            x = self.pixel_x
            y = self.pixel_y

            # find the new pixel that should be shown
            self.pixel_x = self._datetime.get_minute()
            self.pixel_y = self._datetime.get_hour()

            # If the pixel has changed then hide the old one and show the new one.
            if x != self.pixel_x or y != self.pixel_y:
                # turn off original pixel
                self._weather_display.hide_pixel(x, y)
                #display another pixel.
                self._weather_display.show_pixel(self.pixel_x, self.pixel_y)
        return self._datetime.is_display_on
    

    def _apply_reading(self, field, weather, method):
        # TODO add a log message that field was not found.
        if field in weather['current_conditions'].keys():
            method(weather['current_conditions'][field])


    def scroll_label(self, key_input):
        self._weather_display.scroll_label(key_input)


    def weather_complete(self) -> bool:
        return not self._weather_display.scroll_queue


    def display_off(self):
        self._datetime.is_display_on = False
