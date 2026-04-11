import time
from collections import deque

class RateLimiter:
    """
    A simple rate limiter using a sliding window of timestamps.
    """
    def __init__(self, max_calls: int, period_seconds: float):
        self.max_calls = max_calls
        self.period_seconds = period_seconds
        self.calls = deque()

    def is_allowed(self) -> bool:
        """
        Returns True if a call is allowed within the rate limit window.
        """
        now = time.time()
        # Remove timestamps outside the current window
        while self.calls and self.calls[0] <= now - self.period_seconds:
            self.calls.popleft()

        return len(self.calls) < self.max_calls

    def record_call(self):
        """
        Logs a call timestamp.
        """
        self.calls.append(time.time())

# Module-level singleton as requested
DEFAULT_LIMITER = RateLimiter(max_calls=30, period_seconds=10)
