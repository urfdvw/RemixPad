
import board
import busio
import displayio
import i2cdisplaybus
from terminalio import FONT
import adafruit_displayio_ssd1306
from adafruit_display_text.label import Label
from adafruit_display_text import wrap_text_to_lines

class MacroPadDisplay:
    def __init__(self, display):
        self.display = display
        self.splash = displayio.Group()
        self.display.root_group = self.splash

        self.layer_group = displayio.Group()
        self.splash.append(self.layer_group)
        self.layer_group.hidden = False
        self.layer_lable = Label(
            FONT,
            text='',
        )
        self.layer_group.append(self.layer_lable)

        self.macro_group = displayio.Group()
        self.splash.append(self.macro_group)
        self.macro_group.hidden = True
        self.macro_lable = Label(
            FONT,
            text='',
            scale=2,
        )
        self.macro_group.append(self.macro_lable)

        self.layer = -1
        self.state = 0

    def show_small_text(self, text):
        if (self.layer_lable.text == text
        and self.state == 0):
            return
        self.state = 0
        self.layer_lable.text = text
        self.layer_group.hidden = False
        self.macro_group.hidden = True

    def show_big_text(self, text):
        if (self.macro_lable.text == text
        and self.state == 1):
            return
        self.state = 1
        self.macro_lable.text = text
        self.layer_group.hidden = True
        self.macro_group.hidden = False


class MONO_128x32(MacroPadDisplay):
    def __init__(self, display):
        super().__init__(display)
        
        self.layer_lable.color=0xFFFFFF
        self.layer_lable.background_color=0x000000
        self.layer_lable.x=0
        self.layer_lable.y=5
        self.layer_lable.line_spacing=0.8

        self.macro_lable.color=0xFFFFFF
        self.macro_lable.background_color=0x000000
        self.macro_lable.x=0
        self.macro_lable.y=15
        
        self.show_big_text('')
    
    def show_big(self, text):
        self.show_big_text(text)
        
    def show_small(self, text):
        out = '\n'.join(wrap_text_to_lines(text, 128 // 6))
        self.show_small_text(out)
        
displayio.release_displays()
i2c = busio.I2C(board.GP17, board.GP16, frequency=int(1e6))
display_bus = i2cdisplaybus.I2CDisplayBus(i2c, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=32, rotation=180)
macropaddisp = MONO_128x32(display)

# macropaddisp.show_big('Hello')
macropaddisp.show_small('Hello world Hello world Hello world Hello world Hello world Hello world Hello world Hello world')

while 1: 
    pass