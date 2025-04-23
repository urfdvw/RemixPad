"""Signal processing helpers"""
from math import fmod

class AccumulatedInt:
    """
    Accumulates floating-point values and extracts integer parts.

    Attributes:
        accumulation (float): Current accumulated value.
        fast_turn (bool): If True, resets accumulation on sign change of input.
    """
    def __init__(self, fast_turn=True):
        """
        Initialize an AccumulatedInt instance.

        Args:
            fast_turn (bool): If True, quickly resets accumulation when sign flips.
        """
        self.accumulation = 0.0
        self.fast_turn = fast_turn

    def __call__(self, new):
        """
        Add a new value to the accumulation and return the integer part.

        Args:
            new (float): The value to accumulate.

        Returns:
            int: The extracted integer part of the accumulation.
        """
        if self.fast_turn and new * self.accumulation < 0:
            self.accumulation = new
        else:
            self.accumulation += new
        remaining = fmod(self.accumulation, 1)
        int_part = self.accumulation - remaining
        self.accumulation = remaining
        return int(int_part)

class Limit:
    """
    Clamps a value between specified lower and upper bounds.

    Attributes:
        lower (float): Lower limit.
        upper (float): Upper limit.
    """
    def __init__(self, lower, upper):
        """
        Initialize a Limit instance.

        Args:
            lower (float): Lower bound.
            upper (float): Upper bound.
        """
        self.lower = lower
        self.upper = upper

    def __call__(self, val):
        """
        Clamp the input value between lower and upper bounds.

        Args:
            val (float): Value to be clamped.

        Returns:
            float: Clamped value.
        """
        if val > self.upper:
            return self.upper
        if val < self.lower:
            return self.lower
        return val

class State:
    """
    Maintains and updates signal state with optional low-pass filtering and relay logic.

    Attributes:
        id (any): Optional identifier for the state.
        _now (float): Current internal state value.
        last (float): Previous state value.
        use_filter (bool): Whether filtering is enabled.
        alpha (float): Filter coefficient (if used).
        use_relay (bool): Whether relay logic is enabled.
        relay (Relay): Relay object (only if relay threshold is provided).
    """
    def __init__(self, filter_level=None, relay_thr=None, id=None):
        """
        Initialize a State instance.

        Args:
            filter_level (int, optional): Power-of-two filter strength.
            relay_thr (float, optional): Threshold for relay triggering.
            id (any, optional): Identifier for this state.
        """
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
        """
        Get the current state value.

        Returns:
            float: Current state.
        """
        return self._now

    @now.setter
    def now(self, new):
        """
        Update the state with optional filtering and relay behavior.

        Args:
            new (float): New input value.
        """
        self.last = self._now
        # Low-pass filter
        if self.use_filter:
            new = new * self.alpha + self._now * (1 - self.alpha)
        # Relay logic
        diff = new - self.last
        new = self.last + (self.relay(diff) if self.use_relay else diff)
        self._now = new

    @property
    def diff(self):
        """
        Get the difference between current and previous state.

        Returns:
            float: Difference (delta) between current and last values.
        """
        return self._now - self.last
