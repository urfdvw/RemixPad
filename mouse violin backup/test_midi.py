# py native
import time

# board native
import board
import touchio
from usb_host_hid import UsbHostHid
import usb_midi 

# installed lib
import adafruit_midi
from adafruit_midi.control_change import ControlChange
from adafruit_midi.control_change_values import VOLUME
from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff

# custom
from utils import State, Clamp, Slow

#%% setup touch driver
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

#%% setup midi driver

# Set up MIDI over USB
midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=0)

# Global volume fade-in using Control Change 7
vol = 64
volclamp = Clamp(0, 127)
volslow = Slow(0.9)

#%% notes

C4 = 60

scale = [0, 2, 4, 5, 7, 9, 11]



notes = [] # base notes on each button

for i in range(3):
    notes += [C4 + i * 12 + step for step in scale]

# chord

chords = [[0, 2, 4]]

for i in range(1, 7):
    chords.append([note + 1 for note in chords[-1]])
chords[-1].append(chords[-1][-1] + 1) # G7
print(chords)
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
print("test touch guitar")
midi.send(ControlChange(VOLUME, vol))


#%% emulated movements
dist = 0
while True:
    # evt_queue = usb_client_device.events
    # if evt_queue:
    #     mouse_event = evt_queue.popleft()  # FIFO
    #     if mouse_event['x'].now:
    #         vol = volclamp(abs(int(volslow(mouse_event['x'].now))))
    # else:
    #     vol = volclamp(abs(int(volslow(0))))
    # # print(vol)
    # midi.send(ControlChange(VOLUME, vol))
        
    for i in range(len(touch_pads)):
        touch_states[i].now = 1 * touch_pads[i].value
        if touch_states[i].diff == 1:
            for note in chords[i % 7]:
                midi.send(NoteOn(scale[note % 7] + C4 + 12 * (i // 7), 100))
            print(str(i) + " pressed!")
        if touch_states[i].diff == -1:
            for note in chords[i % 7]:
                midi.send(NoteOff(scale[note % 7] + C4 + 12 * (i // 7), 100))
            print(str(i) + " released!")

