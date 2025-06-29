import touchio
import board
from utils import State, Clamp, Slow
from time import sleep

import time
import usb_midi
import adafruit_midi
from adafruit_midi.control_change import ControlChange
from adafruit_midi.control_change_values import VOLUME
from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff

from usb_host_hid import UsbHostHid 

#%% setup tuch
pins = [
    board.GP3,
    board.GP7,
    board.GP11,
    board.GP15, # need re soldering
    board.GP14,
    board.GP2,
    board.GP6,
    board.GP10,
    board.GP9,
    board.GP13,
    board.GP1,
    board.GP0,
    board.GP4,
    board.GP8,
    board.GP12,
]

touch_pads = [
    touchio.TouchIn(pin)
    for pin in pins
]

touch_states = [
    State()
    for i in pins
]

#%% setup midi

# Set up MIDI over USB
midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=0)

# Notes (C major scale): me = E4, do = C4, so = G4
C4 = 60

scale = [0, 2, 4, 5, 7, 9, 11]

Notes = [] 

for i in range(3):
    Notes += [C4 + i * 12 + step for step in scale]

# Sequence: me-me-me-do-me-so
sequence = Notes

# Global volume fade-in using Control Change 7
Vol = 100
volclamp = Clamp(0, 127)
volslow = Slow(0.9)

#%% set up usb host
usb_client_device = UsbHostHid(board.GP21, board.GP22)
while True:
    if usb_client_device.scan():
        break
    else:
        print('failed')
        while True:
            pass
usb_client_device.set_endpoint(0x82)

#%% test midi

# Play the sequence with fixed velocity (volume already handled globally)
for note in []:# sequence:
    midi.send(NoteOn(note, 100))  # 100 = velocity
    time.sleep(0.3)
    midi.send(NoteOff(note, 0))
    time.sleep(0.05)
#%% test if touched
print("test touch")
while True:
    evt_queue = usb_client_device.events
    if evt_queue:
        mouse_event = evt_queue.popleft()  # FIFO
        if mouse_event['x'].now:
            vol = volclamp(abs(int(volslow(mouse_event['x'].now))))
    else:
        vol = volclamp(abs(int(volslow(0))))
    # print(vol)
    midi.send(ControlChange(VOLUME, vol))
        
    for i in range(len(touch_pads)):
        touch_states[i].now = 1 * touch_pads[i].value
        if touch_states[i].diff == 1:
            midi.send(NoteOn(Notes[i], 100))  # 100 = velocity
            print(str(i) + " pressed!")
        if touch_states[i].diff == -1:
            print(str(i) + " released!")
            midi.send(NoteOff(Notes[i], 0))  # 100 = velocity

