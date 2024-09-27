#!/usr/bin/python3.7
import datetime, struct, time, crcmod

from bsp.v1._generic.interfaces import ParameterBase

from typing import List
from dataclasses import dataclass, field


@dataclass
class SamplesFrom(ParameterBase):
    date: datetime.datetime

    def get_raw(self) -> List[int]:
        date_lst = list(struct.pack("<L", int(time.mktime(self.date.astimezone().timetuple()))))

        return date_lst


@dataclass
class StandaloneMode(ParameterBase):
    date: datetime.datetime = field(init=False)
    sampling_time: int
    samples_to_reset: int
    salinidad: float

    def __post_init__(self):
        self.date = datetime.datetime.now(tz=datetime.timezone.utc).astimezone()
        self.execution_id =  int(time.mktime(self.date.astimezone().timetuple()))

        if 1 > self.sampling_time > 255:
            self.valid = False
            return

        if 0 > self.samples_to_reset > 255:
            self.valid = False
            return

        if 0 > self.salinidad > 42:
            self.valid = False
            return

        self.valid = True

    def get_raw(self) -> List[int]:
        self.date = datetime.datetime.now(tz=datetime.timezone.utc).astimezone()
        self.execution_id = int(time.mktime(self.date.astimezone().timetuple()))

        date_lst = list(struct.pack("<L", int(time.mktime(self.date.astimezone().timetuple()))))
        sal_lst = list(struct.pack(">f", self.salinidad))

        crc32_func = crcmod.mkCrcFun(poly=0x18005, rev=True, initCrc=0xFFFF, xorOut=0x0000)
        crc = crc32_func(bytearray([0x01, 0x10, 0x00, 0x75, 0x00, 0x02, 0x04] + sal_lst))
        crc_lst = list(struct.pack("<H", crc))

        return date_lst + [self.sampling_time, self.samples_to_reset] + sal_lst + crc_lst


@dataclass
class OxygenMode(StandaloneMode):
    threshold_high: float
    threshold_low: float
    slaves: int

    def __post_init__(self):
        super().__post_init__()

        if not self.valid:
            return

        if 0 > self.slaves > 6:
            self.valid = False
            return

        try:
            a = list(struct.pack("<f", self.threshold_high))
            a = list(struct.pack("<f", self.threshold_low))
            self.valid = True
        except Exception as e:
            self.valid = False

    def get_raw(self) -> List[int]:
        th_h_lst = list(struct.pack("<f", self.threshold_high))
        th_l_lst = list(struct.pack("<f", self.threshold_low))

        return super().get_raw() + th_h_lst + th_l_lst + [self.slaves]
