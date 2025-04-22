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

#%% ------------------------ EXAMPLE MAIN LOGIC ------------------------

# 1. Instantiate the object
usb_client_device = UsbHostHid(board.GP0, board.GP1)

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
            if mouse_event['back'] and mouse_event['forward']:
                out_h = kbd_int(mouse_event['x'] * kbd_speed)
                for event_i in range(abs(out_h)):
                    if out_h < 0:
                        keyboard.send(Keycode.LEFT_ARROW)
                    else:
                        keyboard.send(Keycode.RIGHT_ARROW)
                out_v = mouse_event['wheel_v']
                for event_i in range(abs(out_v)):
                    if out_v > 0:
                        keyboard.send(Keycode.UP_ARROW)
                    else:
                        keyboard.send(Keycode.DOWN_ARROW)
                    
            elif mouse_event['back']:
                mouse.move(
                    wheel=scroll_int(
                        scroll_direction * scroll_speed * speed_curve(diag_len(mouse_event['x'], mouse_event['y']))
                    )
                )
            elif mouse_event['forward']:
                mouse.move(
                    wheel=scroll_int(
                        -scroll_direction * scroll_speed * speed_curve(diag_len(mouse_event['x'], mouse_event['y']))
                    )
                )
            else:
                mouse.move(
                    x=mouse_event['x'],
                    y=mouse_event['y'],
                    wheel=scroll_direction*mouse_event['wheel_v'],
                )

            left.now = mouse_event['left']
            right.now = mouse_event['right']
            middle.now = mouse_event['middle']

            if left.diff == 1:
                mouse.press(Mouse.LEFT_BUTTON)
            elif left.diff == -1:
                mouse.release(Mouse.LEFT_BUTTON)

            if right.diff == 1:
                mouse.press(Mouse.RIGHT_BUTTON)
            elif right.diff == -1:
                mouse.release(Mouse.RIGHT_BUTTON)

            if middle.diff == 1:
                mouse.press(Mouse.MIDDLE_BUTTON)
            elif middle.diff == -1:
                mouse.release(Mouse.MIDDLE_BUTTON)