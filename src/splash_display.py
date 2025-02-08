import terminalio
import displayio

from adafruit_display_text import bitmap_label

class SplashDisplay(displayio.Group):
    def __init__(self, splash_file, version) -> None:
        super().__init__()
        ICON_X = 2
        ICON_Y = 1
        DISPLAY_WIDTH = 64
        DISPLAY_HEIGHT = 32
        try:
            icon = displayio.OnDiskBitmap(open(splash_file, "rb"))
            print("Icon width:", icon.width)
            print("Icon height:", icon.height)
            bg = displayio.TileGrid(
                icon,
                pixel_shader=getattr(icon, 'pixel_shader', displayio.ColorConverter()),
                tile_width=26,
                tile_height=30,
                x=ICON_X,
                y=ICON_Y
            )
            self.append(bg)
        except Exception as e:
            print('Error loading icon:', e)

        version_label = bitmap_label.Label(terminalio.FONT, color=0x00DD00)
        version_label.text = f'{version.get_version_string()}'
        version_label.anchor_point = (1.0, 1.0)
        version_label.anchored_position = (DISPLAY_WIDTH, DISPLAY_HEIGHT)

        self.append(version_label)
