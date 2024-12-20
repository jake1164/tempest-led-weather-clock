import os
import board
from digitalio import DigitalInOut, Direction

#if(os.getenv('BOARD') == 'PICO-W'):
#    from boards.pico_w import BUZZ_PIN
#elif(os.getenv('BOARD') == 'S2-PICO'):
#    from boards.s2_pico import BUZZ_PIN
#elif(os.getenv('BOARD') == 'S3-PICO'):
#    from boards.s3_pico import BUZZ_PIN
#else:
#    raise Exception("No board defined in settings.toml file.")

class Buzzer:
    def __init__(self, settings) -> None:
        """ Setup the buzzer and initate values stored by class """
        #self._buzzer = DigitalInOut(BUZZ_PIN)
        self._buzzer = DigitalInOut(board.GP27)
        self._buzzer.direction = Direction.OUTPUT
        self._settings = settings
        self._start_beep = False
        self.beep_count = 0


    def buzzer_start(self):
        """ Start the buzzing sound """
        self._buzzer.value = True


    def buzzer_stop(self):
        """ Stop the buzzing sound """
        self._buzzer.value = False

    def judgment_buzzer_switch(self):    
        if self.is_beeping():
            self.buzzer_start()
        self._start_beep = True

    def three_beep(self):
        """ beep over the cource of 3 ticks """
        if self.is_beeping():
            self.judgment_buzzer_switch()
            self.beep_count += 1
            if self.beep_count == 3:
                self.buzzer_stop()
                self.beep_count = 0
                self._start_beep = False

    def is_beeping(self):
        return self._start_beep and self._settings.beep