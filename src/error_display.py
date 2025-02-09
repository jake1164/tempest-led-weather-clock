import terminalio
import displayio

from adafruit_display_text.scrolling_label import ScrollingLabel

class ErrorDisplay(displayio.Group):
    def __init__(self, error_file, description) -> None:
        super().__init__()
        ICON_X = 1
        ICON_Y = 1
        DISPLAY_WIDTH = 64
        DISPLAY_HEIGHT = 32

        try:
            
            icon = displayio.OnDiskBitmap(open(error_file, "rb"))
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
            text=description,
            max_characters=len(description),
            animate_time=0.3
        )
        self.error_label.anchor_point = (1.0, 1.0)
        self.error_label.anchored_position = (DISPLAY_WIDTH, DISPLAY_HEIGHT)
        self.append(self.error_label)

    def scroll(self) -> None:
        self.error_label.update()

