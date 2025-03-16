import terminalio
import displayio

from adafruit_display_text.scrolling_label import ScrollingLabel

class CommonDisplay(displayio.Group):
    def __init__(self, icon_file, message) -> None:
        super().__init__()
        ICON_X = 1
        ICON_Y = 1
        DISPLAY_WIDTH = 64
        DISPLAY_HEIGHT = 32

        try:
            icon = displayio.OnDiskBitmap(icon_file)
            image_width = icon.width
            image_height = icon.height
            
            bg = displayio.TileGrid(
                icon,
                pixel_shader=getattr(icon, 'pixel_shader', displayio.ColorConverter()),
                width=1,
                height=1,
                tile_width=image_width,
                tile_height=image_height,
                x=ICON_X,
                y=ICON_Y
            )
            self.append(bg)
        except Exception as e:
            print('Error loading icon:', e)

        self.error_label = ScrollingLabel(
            terminalio.FONT, 
            color=0xFFFF00,  # Yellow color
            text=message,
            max_characters=len(message),
            animate_time=0.8
        )
        self.error_label.anchor_point = (1.0, 1.0)
        self.error_label.anchored_position = (DISPLAY_WIDTH, DISPLAY_HEIGHT)
        self.append(self.error_label)
        self.error_label.update()


    def scroll(self) -> None:
        self.error_label.update()

