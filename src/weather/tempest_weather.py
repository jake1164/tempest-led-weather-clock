# Pulls weather from a the weatherflow api (from a tempest weather station) 
# https://weatherflow.github.io/Tempest/api/ 
import os

DEBUG = False
STATIONS_URL = 'https://swd.weatherflow.com/swd/rest/stations?token={}'
BETTER_URL = 'https://swd.weatherflow.com/swd/rest/better_forecast?station_id={}&units_temp={}&units_wind={}&units_pressure={}&units_precip={}&units_distance={}&token={}'

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
    def __init__(self, weather_display, network, datetime) -> None:
        self._weather_display = weather_display
        self._network = network
        self._datetime = datetime

        #self._url = BETTER_URL.format(station, token)
        self._url= self._setup_url()
        self._missed_weather = 0
        self.skip = 0
        self.pixel_x = 0
        self.pixel_y = 0


    def _setup_url(self) -> str:
        token = os.getenv('TEMPEST_API_TOKEN')
        station = os.getenv('TEMPEST_STATION')

        if token is None or station is None:
            raise Exception('Missing required TEMPEST environment variables for Tempest API')

        default_units = os.getenv('UNITS')
        if default_units is not None and default_units not in ['metric', 'imperial']:
            raise Exception('Missing required UNITS environment variables')

        temp = self._get_units('UNITS_TEMP', ['f', 'c'], default_units)
        wind = self._get_units('UNITS_WIND', ['mph', 'kph', 'kts', 'mps', 'bft', 'lfm'], default_units)
        pressure = self._get_units('UNITS_PRESSURE', ['inhg', 'mb', 'mmhg', 'hpa'], default_units)
        precip = self._get_units('UNITS_PRECIP', ['in', 'mm', 'cm'], default_units)
        distance = self._get_units('UNITS_DISTANCE', ['mi', 'km'], default_units)

        return BETTER_URL.format(station, temp, wind, pressure, precip, distance, token)


    def _get_units(self, setting: str, valid_units, default_unit: str) -> str:
        unit = os.getenv(setting)
        if unit is None:
            if default_unit == "metric":
                unit = valid_units[1]
            else:
                unit = valid_units[0]
        elif unit not in valid_units:
            raise ValueError(f"Invalid units: {unit}. Must be one of {valid_units}")
        return unit

    def get_update_interval(self) -> int:
        """ Returns the weather update interval in seconds """
        return 20


    def get_weather(self) -> dict:
        weather = self._network.getJson(self._url)
        #print(weather)
        # TODO: reduce size of json data and purge gc
        return weather


    def _apply_reading(self, weather, field: tuple, func, format="{field1}", formatData=None) -> None:
        if isinstance(field[0], int) and isinstance(weather, list) and field[0] < len(weather):
            self._apply_reading(weather[field[0]], field[1:], func, format, formatData)
        elif field and field[0] in weather:
            try:
                if(len(field) > 1):
                    self._apply_reading(weather[field[0]], field[1:], func, format, formatData)
                else:
                    if formatData is None:
                        formatData = {}

                    if field[0] == 'icon':
                        icon = ICON_MAP.get(weather[field[0]], 'CLEAR_DAY')
                        func(icon)
                    else:
                        func(format.format(field1=weather[field[0]], **formatData))
            except Exception as ex:
                print('Unable to apply reading', ex)


    def show_weather(self):
        try:
            weather = self.get_weather()
        except Exception as ex:
            print('unable to get weather', ex)
            weather = None

        # Always add the date so there is something to scroll. 
        self._weather_display.add_scroll_text(
            self._datetime.get_date()
        )

        if not weather or 'current_conditions' not in weather or len(weather['current_conditions']) == 0:
            if self._missed_weather > 10:
                import microcontroller
                # restart the device
                self._weather_display.add_scroll_text("Restarting device")
                self._weather_display.show()
                microcontroller.reset()
                return
            
            if self._missed_weather > 5 and self._missed_weather < 10: 
                self._weather_display.hide_temperature()
                self._weather_display.add_scroll_text("Unable to contact API")
            # else if 10 updates then restart the device?
            else:
                self._missed_weather += 1
            
            self._weather_display.show() #TODO: is this required?
            return
        else: 
            self._missed_weather = 0

        try:
            if DEBUG:
                print(weather['current_conditions'])

            self._apply_reading(weather, 
                                ('current_conditions', 'icon'), 
                                self._weather_display.set_icon
                                )
            self._apply_reading(weather, ('current_conditions', 'air_temperature'), 
                                self._weather_display.set_temperature, 
                                "{field1:.0f}°{field2}", 
                                {'field2': weather['units']['units_temp']}
                                )

            # TODO: Make these generic display methods to add to the QUEUE.  
            # Note we need to be sure to wait for the display to catch up?  or only update the temperature until QUEUE is empty?
            self._apply_reading(weather, 
                                ('current_conditions', 'relative_humidity'), 
                                self._weather_display.add_scroll_text, 
                                "{field1}% humidity"
                                )
            self._apply_reading(weather, 
                                ('current_conditions', 'feels_like'), 
                                self._weather_display.add_scroll_text, 
                                "Feels Like {field1:.0f}°{field2}", 
                                {'field2': weather['units']['units_temp']}
                                )
            self._apply_reading(weather, 
                                ('current_conditions', 'wind_avg'), 
                                self._weather_display.add_scroll_text,  
                                "Wind {field1:.1f} {field2}" , 
                                {'field2': weather['units']['units_wind']}
                                )
            self._apply_reading(weather, 
                                ('current_conditions', 'conditions'), 
                                self._weather_display.add_scroll_text
                                )
            
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


    def scroll_label(self, key_input) -> None:
        self._weather_display.scroll_label(key_input)


    def weather_complete(self) -> bool:
        return not self._weather_display.scroll_queue


    def display_off(self) -> None:
        self._datetime.is_display_on = False
