from math import fmod

class AccumulatedInt:
    def __init__(self):
        self.accumulation = 0.0

    def __call__(self, new):
        self.accumulation += new
        # remaining = fmod(self.accumulation, 1)
        remaining = self.accumulation % 1
        int_part = self.accumulation - remaining
        self.accumulation = remaining
        return int(int_part)

class State:
    def __init__(
        self, filter_level=None, relay_thr=None, id=None
    ):
        self.id = id
        self._now = 0
        self.last = 0
        if filter_level is not None:
            self.use_filter = True
            self.alpha = 1 / 2**filter_level
        else:
            self.use_filter = False
        if relay_thr is not None:
            self.use_relay = True
            self.relay = Relay(relay_thr)
        else:
            self.use_relay = False

    @property
    def now(self):
        return self._now

    @now.setter
    def now(self, new):
        self.last = self._now
        # low pass filter
        if self.use_filter:
            new = new * self.alpha + self._now * (1 - self.alpha)
        # Relay
        diff = new - self.last
        new = self.last + (self.relay(diff) if self.use_relay else diff)
        self._now = new

    @property
    def diff(self):
        return self._now - self.last
