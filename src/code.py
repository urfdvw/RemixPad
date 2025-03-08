import array
import board
import time
import usb.core
import usb_host
import adafruit_usb_host_descriptors
import struct
import collections

def to_signed_8(val):
    """Helper to convert an unsigned byte (0-255) to signed (-128 to 127)."""
    return struct.unpack("b", bytes([val]))[0]

class UsbHostHid:
    def __init__(self, d_plus, d_minus):
        """Initialize the USB host on the specified D+ and D- pins."""
        self._port = usb_host.Port(d_plus, d_minus)
        self._device = None
        self._endpoint = None

        # Buffer for reading reports
        self._buf = array.array("B", [0] * 64)

        # Store the last report to avoid duplicating unchanged data
        self._prev_report = None

        # Queue to store parsed “mouse event” dictionaries (maxlen = 100)
        self._events = collections.deque([], 100)

        # Optionally ignore “noisy” indexes in the report
        self._ignore_indexes = []

    def _reports_equal(self, a, b):
        """Return True if two reports are the same, ignoring self._ignore_indexes."""
        if (a is None) != (b is None):
            return False
        for i in range(len(a)):
            if i not in self._ignore_indexes:
                if a[i] != b[i]:
                    return False
        return True

    def scan(self):
        """
        Scan all connected USB devices, print descriptor information, and
        store the first device found as self._device.
        Also sets configuration and detaches kernel driver if necessary.
        """
        for d in usb.core.find(find_all=True):
            # Print descriptors for each device
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
                    print(" value {}".format(cfg_value))
                elif desc_type == adafruit_usb_host_descriptors.DESC_INTERFACE:
                    intf_num = config_desc[idx + 2]
                    cls = config_desc[idx + 5]
                    subcls = config_desc[idx + 6]
                    print(" interface[{}]".format(intf_num))
                    print("  class {:02x} subclass {:02x}".format(cls, subcls))
                elif desc_type == adafruit_usb_host_descriptors.DESC_ENDPOINT:
                    ep_addr = config_desc[idx + 2]
                    if ep_addr & 0x80:
                        print("  IN  0x{:02x}".format(ep_addr))
                    else:
                        print("  OUT 0x{:02x}".format(ep_addr))
                idx += desc_len

            # If we don't already have a device, choose the first enumerated
            if self._device is None:
                self._device = d

        # If we found a device, configure it
        if self._device:
            self._device.set_configuration()
            # Single-line .format() to avoid multiline f-string issues
            print(
                "Configuration set for {}, {}, {}".format(
                    self._device.manufacturer,
                    self._device.product,
                    self._device.serial_number
                )
            )
            # Detach kernel driver if necessary (Linux-specific)
            if self._device.is_kernel_driver_active(0):
                self._device.detach_kernel_driver(0)

    def set_endpoint(self, endpoint):
        """Set the endpoint we will read from (e.g. 0x81, 0x82, etc.)."""
        self._endpoint = endpoint
        print("Monitoring endpoint 0x{:02x} for mouse data...".format(endpoint))

    @property
    def events(self):
        """
        Attempt to read a single report from the configured endpoint (non-blocking).
        If there’s a new report, parse it as a mouse event and enqueue it in _events.
        Return the underlying event deque.
        """
        if not self._device or self._endpoint is None:
            return self._events

        try:
            count = self._device.read(self._endpoint, self._buf)
        except usb.core.USBTimeoutError:
            return self._events  # No new data this time

        if count < 3:
            return self._events  # Not enough bytes for a standard mouse packet

        # Compare with previous report to avoid duplicates
        if not self._reports_equal(self._buf, self._prev_report):
            # Parse the mouse report
            button_byte = self._buf[0]
            x_move = to_signed_8(self._buf[1])
            y_move = to_signed_8(self._buf[2])

            wheel_vertical = 0
            if count >= 4:
                wheel_vertical = to_signed_8(self._buf[3])  # scroll wheel

            # Typical button bits in many 5-button mice:
            left_button   = (button_byte & 0x01) != 0
            right_button  = (button_byte & 0x02) != 0
            middle_button = (button_byte & 0x04) != 0
            back_button   = (button_byte & 0x08) != 0
            forward_button= (button_byte & 0x10) != 0

            # Create an “event” dictionary
            event = {
                "left": left_button,
                "right": right_button,
                "middle": middle_button,
                "back": back_button,
                "forward": forward_button,
                "x": x_move,
                "y": y_move,
                "wheel_v": wheel_vertical
            }
            self._events.append(event)

        self._prev_report = self._buf[:]
        return self._events


# ------------------------ EXAMPLE MAIN LOGIC ------------------------

# 1. Instantiate the object
usb_client_device = UsbHostHid(board.TX, board.RX)

# 2. Scan devices to set up self._device
usb_client_device.scan()

# 3. Set the monitored endpoint (adjust if needed)
usb_client_device.set_endpoint(0x82)

print("Entering main event loop...")

while True:
    # 4. Poll the .events property to check for new mouse data
    evt_queue = usb_client_device.events

    # If any new events are available, pop and process them
    if evt_queue:
        mouse_event = evt_queue.popleft()  # FIFO
        # Show the event with multiple print-arguments + trailing commas
        print(
            "Got mouse event: ",
            mouse_event,
        )
    time.sleep(0.01)
