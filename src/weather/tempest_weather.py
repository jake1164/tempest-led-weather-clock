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
    def __init__(self, network, units) -> None:
        self._units = units
        self._network = network
        token = os.getenv('TEMPEST_API_TOKEN')
        station = os.getenv('TEMPEST_STATION')
        #self._url = URL.format(station, token)
        self._url = BETTER_URL.format(station, token)
        self._missed_weather = 0


    def get_weather(self):
        weather = self._network.getJson(self._url)
        #print(weather)
        # TODO: reduce size of json data and purge gc

        return weather


    def get_update_interval(self):
        """ Returns the weather update interval in seconds """
        return 20

    def show_weather(self, weather_display):
        try:
            weather = self.get_weather()            
        except Exception as ex:
            print('unable to get weather', ex)
            weather = None

        if weather == {} or weather['current_conditions'] == None or len(weather['current_conditions']) == 0:
            if self._missed_weather > 5: 
                weather_display.hide_temperature()
                weather_display.add_text_display("Unable to contact API")
            # else if 10 updates then restart the device?
            else:
                self._missed_weather += 1
            
            weather_display.show() #TODO: is this required?
            return
        else: 
            self._missed_weather = 0

        try:
            print(weather['current_conditions'])
            #TODO  Temperature and icon are the only set fields, everything else goes into a scroll text field
            if 'icon' in weather['current_conditions'].keys():
                # Map tempest weather icon to the standard weather icon
                icon_name = weather['current_conditions'].get('icon', 'clear-day')
                icon = ICON_MAP.get(icon_name, 'CLEAR_DAY')

                weather_display.set_icon(icon)

            self._apply_reading('air_temperature', weather, weather_display.set_temperature)
            
            # TODO: Make these generic display methods to add to the QUEUE.  
            # Note we need to be sure to wait for the display to catch up?  or only update the temperature until QUEUE is empty?
            self._apply_reading('relative_humidity', weather, weather_display.set_humidity)  
            self._apply_reading('feels_like', weather, weather_display.set_feels_like)
            self._apply_reading('wind_avg', weather, weather_display.set_wind)
            self._apply_reading('conditions', weather, weather_display.set_description)
            
            # TODO: In theory I could assume anything else is a straight read from data

        except Exception as ex:
            print('Unable to display weather', ex)
        finally:
            weather_display.show()


    def _apply_reading(self, field, weather, method):
        # TODO add a log message that field was not found.
        if field in weather['current_conditions'].keys():
            method(weather['current_conditions'][field])

    def _convert_temperature(self, celsius):
        if self._units == "imperial":
            return (celsius * 1.8) + 32
        return celsius


    def _convert_windspeed(self, speed):
        if self._units == "imperal":
            return speed * 2.23693629
        return speed