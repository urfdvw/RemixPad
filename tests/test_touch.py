import touchio
import board
from utils import State
from time import sleep

pins = [
    board.GP0,
    board.GP1,
    board.GP2,
    board.GP3,
    board.GP4,
    board.GP5,
    board.GP6,
    board.GP7,
    board.GP8,
    board.GP9,
    board.GP10,
    board.GP11,
    board.GP12,
    board.GP13,
    board.GP14,
    board.GP15,
]

touch_pads = [
    touchio.TouchIn(pin)
    for pin in pins
]

touch_states = [
    State()
    for i in pins
]

#%% test if touched

while True:
    for i in range(len(touch_pads)):
        touch_states[i].now = 1 * touch_pads[i].value
        if touch_states[i].diff == 1:
            print(str(i) + " pressed!")
        if touch_states[i].diff == -1:
            print(str(i) + " released!")
            
#%% test value

names = ['gp'+str(i) for i in range(len(touch_pads))]
while True:
    print("startplot:", 'x', 'y')
    for i in range(16):
        print(i - 0.1, 0)
        print(i, touch_pads[i].raw_value)
        print(i + 0.1, 0)
    sleep(0.2)
