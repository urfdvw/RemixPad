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
curve_k = 3
debug = False
scroll_speed = 0.02
scroll_direction = 1
mouse_speed = 1.5

#%% helper
def diag_len(x, y):
    return sqrt(x * x + y * y)

def speed_curve(x):
    return x if x < curve_thr else (x - curve_thr) / curve_k + curve_thr

#%% states
scroll_int = AccumulatedInt()
x_int = AccumulatedInt()
y_int = AccumulatedInt()
left = State()
right = State()
middle = State()
gesture_mode = State()
gesture_x = 0
gesture_y = 0
gesture_thr = 150

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
                print('double state button pressed, gesture on')
                gesture_mode.now = True
                gesture_x = 0
                gesture_y = 0
                
            if (not (mouse_event['back'].now and mouse_event['forward'].now)) and gesture_mode.now == True:
                print('double state button released, gesture off')
                gesture_mode.now = False
                print(gesture_x, gesture_y)
                if max(abs(gesture_x), abs(gesture_y)) > gesture_thr:
                    if gesture_x < gesture_y and gesture_x < - gesture_y:
                        print('Left')
                        keyboard.press(Keycode.CONTROL)
                        keyboard.send(Keycode.RIGHT_ARROW)
                        keyboard.release(Keycode.CONTROL)
                    if gesture_x > gesture_y and gesture_x > - gesture_y:
                        print('Right')
                        keyboard.press(Keycode.CONTROL)
                        keyboard.send(Keycode.LEFT_ARROW)
                        keyboard.release(Keycode.CONTROL)
                    if gesture_x > gesture_y and gesture_x < - gesture_y:
                        print('Up')
                        keyboard.press(Keycode.CONTROL)
                        keyboard.send(Keycode.UP_ARROW)
                        keyboard.release(Keycode.CONTROL)
                    if gesture_x < gesture_y and gesture_x > - gesture_y:
                        print('Down')
                        keyboard.press(Keycode.CONTROL)
                        keyboard.send(Keycode.DOWN_ARROW)
                        keyboard.release(Keycode.CONTROL)

            if gesture_mode.now:
                gesture_x += mouse_event['x'].now
                gesture_y += mouse_event['y'].now
                

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
                        x=x_int(mouse_speed * mouse_event['x'].now),
                        y=y_int(mouse_speed * mouse_event['y'].now),
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