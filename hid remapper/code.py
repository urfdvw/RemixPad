print('this is the remapper')
# python native
import array
import collections
from math import sqrt
import struct
import time

# board native
import board
import usb.core
import usb_hid
import usb_host

# adafruit
from adafruit_hid.mouse import Mouse
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
import adafruit_usb_host_descriptors

# user
from usb_host_hid import UsbHostHid 
from utils import AccumulatedInt, State

#%% config
curve_thr = 3
curve_k = 1
debug = False
scroll_speed = 0.02
scroll_direction = -1
kbd_speed = 0.01

#%% helper
def diag_len(x, y):
    return sqrt(x * x + y * y)

def speed_curve(x):
    return x if x < curve_thr else (x - curve_thr) / curve_k + curve_thr

#%% states
kbd_int = AccumulatedInt()
scroll_int = AccumulatedInt()
left = State()
right = State()
middle = State()
kbd_mode = False

#%% ------------------------ EXAMPLE MAIN LOGIC ------------------------

# 1. Instantiate the object
usb_client_device = UsbHostHid(board.TX, board.RX)

# 2. Scan devices to set up self._device
while True:
    if usb_client_device.scan():
        break
    else:
        print('retry')

# 3. Set the monitored endpoint (adjust if needed)
usb_client_device.set_endpoint(0x82)
mouse = Mouse(usb_hid.devices)
keyboard = Keyboard(usb_hid.devices)

print("Entering main event loop...")

while True:
    # 4. Poll the .events property to check for new mouse data
    evt_queue = usb_client_device.events

    # If any new events are available, pop and process them
    if evt_queue:
        mouse_event = evt_queue.popleft()  # FIFO
        if debug:
            # Show the event with multiple print-arguments + trailing commas
            print(
                "Got mouse event: ",
                mouse_event,
            )
            time.sleep(0.01)
        else:
            if ((mouse_event['back'].diff == 1 and mouse_event['forward'].now)
            or (mouse_event['back'].now and mouse_event['forward'].diff == 1)):
                kbd_mode = not kbd_mode
                print('keyboard mode: ', kbd_mode)
                continue
            
            if kbd_mode:
                out_h = kbd_int(mouse_event['x'].now * kbd_speed)
                for event_i in range(abs(out_h)):
                    if out_h < 0:
                        keyboard.send(Keycode.LEFT_ARROW)
                    else:
                        keyboard.send(Keycode.RIGHT_ARROW)
                out_v = mouse_event['wheel_v'].now
                for event_i in range(abs(out_v)):
                    if out_v > 0:
                        keyboard.send(Keycode.UP_ARROW)
                    else:
                        keyboard.send(Keycode.DOWN_ARROW)
    
                if mouse_event['left'].diff == 1:
                    keyboard.press(Keycode.LEFT_ARROW)
                elif mouse_event['left'].diff == -1:
                    keyboard.release(Keycode.LEFT_ARROW)
                if mouse_event['right'].diff == 1:
                    keyboard.press(Keycode.RIGHT_ARROW)
                elif mouse_event['right'].diff == -1:
                    keyboard.release(Keycode.RIGHT_ARROW)
                        
            else:
                if mouse_event['back'].now:
                    mouse.move(
                        wheel=scroll_int(
                            scroll_direction * scroll_speed * speed_curve(diag_len(mouse_event['x'].now, mouse_event['y'].now))
                        )
                    )
                elif mouse_event['forward'].now:
                    mouse.move(
                        wheel=scroll_int(
                            -scroll_direction * scroll_speed * speed_curve(diag_len(mouse_event['x'].now, mouse_event['y'].now))
                        )
                    )
                else:
                    mouse.move(
                        x=mouse_event['x'].now,
                        y=mouse_event['y'].now,
                        wheel=scroll_direction*mouse_event['wheel_v'].now,
                    )
                
    
                if mouse_event['left'].diff == 1:
                    mouse.press(Mouse.LEFT_BUTTON)
                elif mouse_event['left'].diff == -1:
                    mouse.release(Mouse.LEFT_BUTTON)
    
                if mouse_event['right'].diff == 1:
                    mouse.press(Mouse.RIGHT_BUTTON)
                elif mouse_event['right'].diff == -1:
                    mouse.release(Mouse.RIGHT_BUTTON)
    
                if mouse_event['middle'].diff == 1:
                    mouse.press(Mouse.MIDDLE_BUTTON)
                elif mouse_event['middle'].diff == -1:
                    mouse.release(Mouse.MIDDLE_BUTTON)