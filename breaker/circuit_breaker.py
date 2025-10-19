import random
from datetime import datetime, timedelta
from functools import wraps
from typing import Callable, Optional, Generator, Any, TypeVar, Awaitable
from enum import Enum


class OpenCircuitException(Exception):
    pass


T = TypeVar("T")
AsyncFunc = Callable[..., Awaitable[T]]

class CircuitBreaker:
    class CircuitState(Enum):
        OPEN = "open"
        CLOSED = "closed"

    @staticmethod
    def _default_retry_strategy() -> Generator[int, None, None]:
        """ Infinite generator yielding backoff + jitter in seconds. """
        base = 1
        cap = 60

        while True:
            jitter = random.randrange(0, base*3)
            yield base+jitter
            base *= 2
            if base > cap:
                base = cap

    def __init__(
        self,
        max_consecutive_errors: int = 5,
        retry_strategy: Optional[Callable[[], Generator[int, None, None]]] = None
    ) -> None:
        self.max_errors: int = max_consecutive_errors
        self.count_errors: int = 0
        self.retry_gen: Generator[int, None, None] = (
            retry_strategy() if retry_strategy else CircuitBreaker._default_retry_strategy()
        )
        self.last_attempt: Optional[datetime] = None

    def __call__(self, circuit: AsyncFunc[T]) -> AsyncFunc[T]:
        @wraps(circuit)
        async def breaker(*args, **kwargs) -> T:
            if self.count_errors >= self.max_errors:
                retry_time = next(self.retry_gen)
                if self.last_attempt and datetime.now() - self.last_attempt < timedelta(seconds=retry_time):
                    raise OpenCircuitException()
            try:
                result = await circuit(*args, **kwargs)
                self.last_attempt = datetime.now()
                self.count_errors = 0
                return result
            except Exception:
                self.count_errors += 1
                self.last_attempt = datetime.now()
                raise
        return breaker
    
    @property
    def state(self) -> "CircuitBreaker.CircuitState":
        return (
            CircuitBreaker.CircuitState.CLOSED
            if self.count_errors <= self.max_errors
            else CircuitBreaker.CircuitState.OPEN
        )