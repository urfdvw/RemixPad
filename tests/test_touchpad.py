import touchio
import board
from utils import State
from time import sleep
from touchbar import TouchBarPhysics

pins = [
    board.GP0,
    board.GP2,
    board.GP4,
    board.GP8,
    board.GP10,
    board.GP12,
]

pads = [
    touchio.TouchIn(pin)
    for pin in pins
]

bar = TouchBarPhysics(
    pads = pads,
    pad_max=[2280, 3824, 2406, 3242, 2170, 2073],
    pad_min=[987, 1216, 1201, 1209, 946, 831],
)

print('startplot:', 'x', 'z')
while True:
    sleep(0.1)
    data = bar.get()
    print(data.x.now , data.z.now)