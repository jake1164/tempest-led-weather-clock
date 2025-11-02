import os
import board
from digitalio import DigitalInOut, Direction

BUZZ_PIN = board.GP27

class Buzzer:
    def __init__(self, settings) -> None:
        """ Setup the buzzer and initiate values stored by class """
        self._buzzer = DigitalInOut(BUZZ_PIN)
        self._buzzer.direction = Direction.OUTPUT
        self._settings = settings
        self._beep_counter = 0
        self._beep_active = False


    def buzzer_start(self):
        """ Start the buzzing sound """
        if self._settings.beep:
            self._buzzer.value = True


    def buzzer_stop(self):
        """ Stop the buzzing sound """
        self._buzzer.value = False
        self._beep_active = False
        self._beep_counter = 0


    def judgment_buzzer_switch(self):    
        """Simple beep for key actions"""
        if self._settings.beep:
            self._beep_active = True
            self._beep_counter = 0
            self.buzzer_start()


    def three_beep(self):
        """ beep for a key press - should be called once per key press """
        if self._settings.beep and not self._beep_active:
            self._beep_active = True
            self._beep_counter = 0
            self.buzzer_start()


    def update(self):
        """Call this regularly from main loop to handle beep timing"""
        if self._beep_active:
            self._beep_counter += 1
            if self._beep_counter >= 3:  # Beep for 3 cycles
                self.buzzer_stop()


    def is_beeping(self):
        return self._beep_active