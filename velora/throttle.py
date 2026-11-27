"""Bounded, process-local budgets for the single-process loopback server."""
import math
from collections import deque
from threading import Lock
from time import monotonic

from werkzeug.exceptions import TooManyRequests


class MinuteBudget:
    def __init__(self, limit):
        self.limit = limit
        self.admitted = deque()
        self.lock = Lock()

    def reserve(self):
        with self.lock:
            now = monotonic()
            while self.admitted and self.admitted[0] <= now - 60:
                self.admitted.popleft()
            if len(self.admitted) >= self.limit:
                retry = math.ceil(self.admitted[0] + 60 - now)
                raise TooManyRequests(retry_after=retry)
            self.admitted.append(now)
