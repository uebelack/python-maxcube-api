from dataclasses import dataclass
from math import inf
from time import time


@dataclass(frozen=True)
class Timeout:
    name: str
    duration: float

    def deadline(self):
        return Deadline(self.name, time() + self.duration)

class Deadline:

    def __init__(self, name: str, deadline: float, *, parent = None):
        self.__name = name
        self.__deadline = deadline
        self.__parent = parent

    def fullname(self) -> str:
        if not self.__parent:
            return self.__name
        return self.__parent.fullname() + ':' + self.__name

    def remaining(self, *, lower_bound: float = 0, upper_bound: float = inf) -> float:
        return min(max(lower_bound, self.__deadline - time()), upper_bound)

    def is_expired(self) -> bool:
        return self.remaining() <= 0

    def subdeadline(self, name, deadline: float) -> 'Deadline':
        return Deadline(name, min(self.__deadline, deadline), parent = self)

    def subtimeout(self, timeout: Timeout) -> 'Deadline':
        return self.subdeadline(timeout.name, time() + timeout.duration)

    def __str__(self) -> str:
        rem = self.remaining(lower_bound=-inf)
        if rem < 0:
            return 'Deadline %s expired %.03f seconds ago' % (self.fullname(), -rem)
        return 'Deadline %s will expire in %.03f seconds' % (self.fullname(), rem)
