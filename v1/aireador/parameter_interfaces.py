#!/usr/bin/python3.7
import datetime, struct, time

from bsp.v1.aireador import methods
from bsp.v1._generic.interfaces import ParameterBase

from typing import List
from dataclasses import dataclass, field


@dataclass
class TimerMode(ParameterBase):
    date: datetime.datetime = field(init=False)
    aireadores: int
    capacitor: bool
    duracion: int

    salidas: int = field(init=False)

    def __post_init__(self):
        if 1 > self.aireadores > 8:
            self.valid = False
            return

        if 1 > self.duracion > 65535:
            self.valid = False
            return

        self.date = datetime.datetime.now(tz=datetime.timezone.utc).astimezone()
        self.salidas = int(self.aireadores / 2) + (self.aireadores % 2 > 0)

        self.valid = True

    def get_raw(self) -> List[int]:
        self.date = datetime.datetime.now(tz=datetime.timezone.utc).astimezone()

        date_lst = list(struct.pack("<L", int(time.mktime(self.date.astimezone().timetuple()))))
        port_out_int = methods.capacitor_to_port_out(self.salidas, self.capacitor)
        port_out_lst = list(struct.pack("<H", port_out_int))
        duracion_lst = list(struct.pack("<H", self.duracion))

        return date_lst + port_out_lst + duracion_lst


@dataclass
class ScheduleMode(ParameterBase):
    date: datetime.datetime = field(init=False)
    aireadores: int
    capacitor: bool
    horarios: List[int]

    salidas: int = field(init=False)

    def __post_init__(self):
        if 1 > self.aireadores > 8:
            self.valid = False
            return

        self.date = datetime.datetime.now(tz=datetime.timezone.utc).astimezone()
        self.salidas = int(self.aireadores / 2) + (self.aireadores % 2 > 0)
        self.valid = True

    def get_raw(self) -> List[int]:
        self.date = datetime.datetime.now(tz=datetime.timezone.utc).astimezone()

        date_lst = list(struct.pack("<L", int(time.mktime(self.date.astimezone().timetuple()))))
        port_out_int = methods.capacitor_to_port_out(self.salidas, self.capacitor)
        port_out_lst = list(struct.pack("<H", port_out_int))

        return date_lst + port_out_lst + self.horarios


@dataclass
class SetCapacitor(ParameterBase):
    capacitor: bool

    def __post_init__(self):
        self.valid = True

    def get_raw(self) -> List[int]:
        return [0 if self.capacitor else 1]
