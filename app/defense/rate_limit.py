from collections import defaultdict, deque
from threading import Lock
from time import monotonic


class RateLimiter:
    def __init__(self, max_attempts: int = 5, window_seconds: int = 60):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self.attempts = defaultdict(deque)
        self.lock = Lock()

    def is_allowed(self, key: str) -> bool:
        now = monotonic()
        cutoff = now - self.window_seconds

        with self.lock:
            timestamps = self.attempts[key]

            # Remove tentativas que saíram da janela de tempo.
            while timestamps and timestamps[0] <= cutoff:
                timestamps.popleft()

            # Se atingiu o limite, rejeita a nova tentativa.
            if len(timestamps) >= self.max_attempts:
                return False

            # Registra a tentativa permitida.
            timestamps.append(now)
            return True


login_limiter = RateLimiter(
    max_attempts=5,
    window_seconds=60,
)
