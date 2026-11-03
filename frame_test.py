import sys
import board, digitalio
from PIL import Image, ImageDraw
from adafruit_rgb_display import st7789

rotation = int(sys.argv[1]) if len(sys.argv) > 1 else 0
y_offset = int(sys.argv[2]) if len(sys.argv) > 2 else 80

bl = digitalio.DigitalInOut(board.D26)
bl.switch_to_output()
bl.value = True

disp = st7789.ST7789(board.SPI(), width=240, height=240, rotation=rotation,
                     x_offset=0, y_offset=y_offset,
                     cs=digitalio.DigitalInOut(board.CE0),
                     dc=digitalio.DigitalInOut(board.D25),
                     rst=digitalio.DigitalInOut(board.D24),
                     baudrate=24000000)

img = Image.new("RGB", (240, 240), (0, 0, 0))
draw = ImageDraw.Draw(img)
draw.rectangle((0, 0, 239, 239), outline=(255, 0, 0), width=4)
draw.text((90, 10), "TOP", fill=(255, 255, 255))
draw.text((85, 220), "BOTTOM", fill=(255, 255, 255))
draw.text((8, 115), "L", fill=(255, 255, 255))
draw.text((225, 115), "R", fill=(255, 255, 255))
draw.text((50, 115), f"rot={rotation} y_off={y_offset}", fill=(0, 255, 0))
disp.image(img)
print("drawn", rotation, y_offset)
