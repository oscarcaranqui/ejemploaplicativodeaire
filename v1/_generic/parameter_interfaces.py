#!/usr/bin/python3.7

import datetime
import struct
import time

from bsp.v1._generic.interfaces import ParameterBase

from typing import List
from dataclasses import dataclass, field

@dataclass
class SyncTime(ParameterBase):
    date: datetime.datetime = field(init=False)

    def __post_init__(self):
        self.date = datetime.datetime.now(tz=datetime.timezone.utc).astimezone()
        self.valid = True

    def get_raw(self) -> List[int]:
        self.date = datetime.datetime.now(tz=datetime.timezone.utc).astimezone()
        date_lst = list(struct.pack("<L", int(time.mktime(self.date.astimezone().timetuple()))))

        return  date_lst