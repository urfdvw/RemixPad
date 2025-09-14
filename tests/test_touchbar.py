import touchio
import board
from utils import State
from time import sleep
from touchbar import TouchBarPhysics

pins = [
    board.GP18,
    board.GP19,
    board.GP20,
    board.GP26,
    board.GP27,
    board.GP28,
]

pads = [
    touchio.TouchIn(pin)
    for pin in pins
]

bar = TouchBarPhysics(
    pads = pads,
    pad_max=[842, 1039, 1029, 1085, 1012, 1252],
    pad_min=[532, 506, 503, 709, 709, 725],
)

print('startplot:', 'x', 'z')
while True:
    sleep(0.1)
    data = bar.get()
    print(data.x.now , data.z.now)