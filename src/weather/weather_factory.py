from . import tempest_weather, open_weather

def Factory(api, weather_display, datetime, network):
    
    apis = {
        "OWM": open_weather.OpenWeather,
        "TEMPEST": tempest_weather.TempestWeather
    }

    if(api == "OWM"):
        primary = apis["OWM"](network, weather_display.units)
        return Weather({ "PRIMARY": primary }, weather_display, datetime)
    elif (api == "TEMPEST"):
        primary = apis["TEMPEST"](network, weather_display.units)
        secondary = apis["OWM"](network, weather_display.units)
        return Weather({ "PRIMARY": primary, "SECONDARY": secondary }, weather_display, datetime)


class Weather():    
    ''' Weather takes a primary and secondary weather api. '''
    def __init__(self, apis, weather_display, datetime) -> None:
        self.SKIP_SECONDARY = 4 # Skip this many times between updates
        self._datetime = datetime
        self._weather_display = weather_display
        self._primary = apis['PRIMARY']
        self._secondary = apis['SECONDARY'] if len(apis) == 2 else None
        self.skip = 0
        self.pixel_x = 0
        self.pixel_y = 0


    def show_weather(self):  
        self._weather_display.set_date(
            self._datetime.get_date()
        )

        self._primary.show_weather(self._weather_display)
        if self._secondary and self.skip == 0: #TODO reduce the frequency of secondary calls
            self.skip = self.SKIP_SECONDARY
            self._secondary.show_secondary(self._weather_display)
        elif self._secondary:
            self.skip -= 1


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


    def get_update_interval(self):
        return self._primary.get_update_interval()


    def scroll_label(self, key_input):
        self._weather_display.scroll_label(key_input)


    def weather_complete(self) -> bool:
        return not self._weather_display.scroll_queue


    def display_off(self):
        self._datetime.is_display_on = False

