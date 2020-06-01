from enum import Enum
from datetime import timedelta
from globalconfig import GlobalConfig


def int_list_to_int(int_list: []) -> int:
    return int(''.join(map(str, int_list)))


class AppState(Enum):
    INIT = 0
    RUNNING = 1
    CONFIG = 2
    ADVANCEDCONFIG = 3
    ADVANCEDTIMER = 4
    PAUSED = 5
    WAITING = 6


class TimeUpdate:
    def __init__(self, hour=-1, min=-1, sec=-1, ms=-1):
        self.hour = hour
        self.min = min
        self.sec = sec
        self.ms = ms

    def get_time_delta(self) -> timedelta:
        return timedelta(hours=int(self.hour),
                         minutes=int(self.min),
                         seconds=int(self.sec),
                         milliseconds=int(self.ms))

    def update_last_update(self, previous) -> bool:
        changed = False

        if self.hour != -1 and previous.hour != self.hour:
            previous.hour = self.hour
            changed = True
        if self.min != -1 and previous.min != self.min:
            previous.min = self.min
            changed = True
        if self.sec != -1 and previous.sec != self.sec:
            previous.sec = self.sec
            changed = True
        if self.ms != -1 and previous.ms != self.ms:
            previous.ms = self.ms
            changed = True
        return changed

    def contains_placeholder(self) -> bool:
        return self.ms == -1 or self.sec == -1 or self.min == -1 or self.hour == -1

    def __str__(self):
        ret = ''
        if GlobalConfig.clock_hour:
            ret += f'{self.hour}:'
        ret += f'{self.min}:{self.sec}'
        if GlobalConfig.clock_ms_digits > 0:
            ret += f'.{self.ms}'
        return ret
