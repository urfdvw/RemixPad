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
kbd_speed = 0.02

#%% helper
def diag_len(x, y):
    return sqrt(x * x + y * y)

def speed_curve(x):
    return x if x < curve_thr else (x - curve_thr) / curve_k + curve_thr

#%% states
v_int = AccumulatedInt()
h_int = AccumulatedInt()
left = State()
right = State()
middle = State()

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
            
            out_h = h_int(mouse_event['x'].now * kbd_speed)
            if not out_h:
                keyboard.release(Keycode.LEFT_ARROW)
                keyboard.release(Keycode.RIGHT_ARROW)
                
            for event_i in range(abs(out_h)):
                if out_h < 0:
                    keyboard.release(Keycode.RIGHT_ARROW)
                    keyboard.press(Keycode.LEFT_ARROW)
                else:
                    keyboard.release(Keycode.LEFT_ARROW)
                    keyboard.press(Keycode.RIGHT_ARROW)
                    
            out_v = v_int(mouse_event['y'].now * kbd_speed)
            if not out_v:
                keyboard.release(Keycode.UP_ARROW)
                keyboard.release(Keycode.DOWN_ARROW)
            for event_i in range(abs(out_v)):
                if out_v < 0:
                    keyboard.release(Keycode.DOWN_ARROW)
                    keyboard.press(Keycode.UP_ARROW)
                else:
                    keyboard.release(Keycode.UP_ARROW)
                    keyboard.press(Keycode.DOWN_ARROW)

            # buttons        
            out_w = mouse_event['wheel_v'].now
            for event_i in range(abs(out_w)):
                if out_w > 0:
                    keyboard.send(Keycode.W)
                else:
                    keyboard.send(Keycode.S)

            if mouse_event['left'].diff == 1:
                keyboard.press(Keycode.A)
            elif mouse_event['left'].diff == -1:
                keyboard.release(Keycode.A)
                
            if mouse_event['right'].diff == 1:
                keyboard.press(Keycode.D)
            elif mouse_event['right'].diff == -1:
                keyboard.release(Keycode.D)
