import usb_hid
import usb_midi

usb_hid.disable()
usb_midi.enable()

#%%

from ide_tools import scan_libs
scan_libs()
