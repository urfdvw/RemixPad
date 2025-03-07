import array
import board
import time
import usb.core
import usb_host
import adafruit_usb_host_descriptors
import struct

def to_signed_8(val):
    """Helper to convert an unsigned byte (0-255) to signed (-128 to 127)."""
    return struct.unpack('b', bytes([val]))[0]

# Create the USB Host port on the specified TX/RX pins
port = usb_host.Port(board.TX, board.RX)

VERBOSE_SCAN = True
DIR_IN = 0x80

# If your mouse has noisy bytes that change constantly,
# you can add their indexes here to ignore them in comparisons.
IGNORE_INDEXES = []

def reports_equal(report_a, report_b):
    """
    Test if two reports are the same, ignoring indexes in IGNORE_INDEXES.
    """
    if (report_a is None) != (report_b is None):
        return False
    for i in range(len(report_a)):
        if i not in IGNORE_INDEXES:
            if report_a[i] != report_b[i]:
                return False
    return True

# -- Optionally print all devices and descriptors --
if VERBOSE_SCAN:
    for d in usb.core.find(find_all=True):
        print("pid", hex(d.idProduct))
        print("vid", hex(d.idVendor))
        print("man", d.manufacturer)
        print("product", d.product)
        print("serial", d.serial_number)
        print("config[0]:")
        config_desc = adafruit_usb_host_descriptors.get_configuration_descriptor(d, 0)
        idx = 0
        while idx < len(config_desc):
            desc_len = config_desc[idx]
            desc_type = config_desc[idx + 1]
            if desc_type == adafruit_usb_host_descriptors.DESC_CONFIGURATION:
                cfg_value = config_desc[idx + 5]
                print(f" value {cfg_value:d}")
            elif desc_type == adafruit_usb_host_descriptors.DESC_INTERFACE:
                intf_num = config_desc[idx + 2]
                cls = config_desc[idx + 5]
                subcls = config_desc[idx + 6]
                print(f" interface[{intf_num}]")
                print(f"  class {cls:02x} subclass {subcls:02x}")
            elif desc_type == adafruit_usb_host_descriptors.DESC_ENDPOINT:
                ep_addr = config_desc[idx + 2]
                if ep_addr & DIR_IN:
                    print(f"  IN  0x{ep_addr:02x}")
                else:
                    print(f"  OUT 0x{ep_addr:02x}")
            idx += desc_len

# -- Grab the first USB device we find --
device = None
while device is None:
    for d in usb.core.find(find_all=True):
        device = d
        break
    time.sleep(0.1)

# -- Set the configuration and claim the interface --
device.set_configuration()
print(
    f"Configuration set for {device.manufacturer}, ",
    f"{device.product}, {device.serial_number}"
)

# Detach kernel driver if necessary (Linux-specific typically)
if device.is_kernel_driver_active(0):
    device.detach_kernel_driver(0)

# -- Allocate buffer for incoming data --
buf = array.array("B", [0] * 64)

# Track the previous report so we only print on changes
prev_report = None

print("Ready to read mouse data...")

while True:
    # Try reading from endpoint 0x82; adjust if your mouse uses a different IN endpoint
    try:
        count = device.read(0x82, buf)
    except usb.core.USBTimeoutError:
        continue  # No data this time around

    # For a 5-button mouse, we might see:
    #   buf[0] = button bits (left, right, middle, forward, back)
    #   buf[1] = X movement (signed)
    #   buf[2] = Y movement (signed)
    #   buf[3] = vertical scroll wheel (signed)
    if count < 3:
        # Not enough bytes to form a meaningful mouse report
        continue

    # Only print if the report changed
    if not reports_equal(buf, prev_report):
        # Parse the mouse report
        button_byte = buf[0]
        x_move = to_signed_8(buf[1])
        y_move = to_signed_8(buf[2])

        wheel_vertical = 0
        if count >= 4:
            wheel_vertical = to_signed_8(buf[3])  # standard scroll wheel

        # Typical button bits in many 5-button mice:
        left_button   = (button_byte & 0x01) != 0
        right_button  = (button_byte & 0x02) != 0
        middle_button = (button_byte & 0x04) != 0
        back_button   = (button_byte & 0x08) != 0
        forward_button= (button_byte & 0x10) != 0

        print(
            f"Mouse event: ",
            f"Left={'Down' if left_button else 'Up'}, ",
            f"Right={'Down' if right_button else 'Up'}, ",
            f"Middle={'Down' if middle_button else 'Up'}, ",
            f"Back={'Down' if back_button else 'Up'}, ",
            f"Forward={'Down' if forward_button else 'Up'}, ",
            f"X={x_move}, Y={y_move}, ",
            f"WheelV={wheel_vertical}"
        )

    prev_report = buf[:]
