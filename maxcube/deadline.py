from dataclasses import dataclass
from math import inf
from time import time


@dataclass(frozen=True)
class Timeout:
    name: str
    duration: float


class Deadline:
    def __init__(self, timeout: Timeout, *, parent=None):
        if parent is None:
            self.__deadline = time() + timeout.duration
        else:
            self.__deadline = min(time() + timeout.duration, parent.__deadline)
        self.__timeout = timeout
        self.__parent = parent

    def name(self) -> str:
        return f"{self.__timeout.name}[{self.remaining():.3g}/{self.__timeout.duration:.3g}]"

    def fullname(self) -> str:
        if self.__parent is None:
            return self.name()
        return self.__parent.fullname() + ":" + self.name()

    def remaining(self, *, lower_bound: float = 0, upper_bound: float = inf) -> float:
        return min(max(lower_bound, self.__deadline - time()), upper_bound)

    def is_expired(self) -> bool:
        return self.remaining() <= 0

    def subtimeout(self, timeout: Timeout) -> "Deadline":
        return Deadline(timeout, parent=self)

    def __str__(self) -> str:
        return "Deadline " + self.fullname()
