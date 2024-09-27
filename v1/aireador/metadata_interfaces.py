#!/usr/bin/python3.7
import struct

from bsp.v1._generic.interfaces import MetadataBase

from typing import List
from dataclasses import dataclass, field, InitVar


@dataclass
class TableroStatus:
    port_in: InitVar[int]
    port_out_live: InitVar[int]

    modo_automatico: bool = field(init=False)
    modo_manual: bool = field(init=False)
    supresor_de_transientes: bool = field(init=False)
    supervisor_de_voltajes: bool = field(init=False)
    confirmacion_grupo: List[bool] = field(init=False, default_factory=list)
    falla_guardamotor: bool = field(init=False)

    capacitor: bool = field(init=False)

    error_tablero: bool = field(init=False)

    def __post_init__(self, port_in, port_out_live):
        self.modo_manual = (1 & port_in != 0)
        self.modo_automatico = (2 & port_in != 0)

        self.supresor_de_transientes = (4 & port_in != 0)
        self.supervisor_de_voltajes = (8 & port_in != 0)
        self.falla_guardamotor = (16 & port_in != 0)

        self.confirmacion_grupo = [
            (32 & port_in != 0),
            (64 & port_in != 0),
            (128 & port_in != 0),
            (256 & port_in != 0)
        ]

        self.capacitor = ((port_out_live >> 4) & 1 == 0)
        self.error_tablero = self.falla_guardamotor or self.supresor_de_transientes or self.supervisor_de_voltajes


@dataclass
class ReadStatus(MetadataBase):
    mode: str = field(init=False)
    port_in: int = field(init=False)
    port_out: int = field(init=False)
    port_out_live: int = field(init=False)

    tablero: TableroStatus = field(init=False)

    def __post_init__(self, data: List[int]):
        if len(data) != 7:
            self.valid = False
            return

        app_mode = [
            "idle",
            "timer",
            "standalone",
            "oxygen"
        ]

        if data[0] > 3:
            self.valid = False
            return

        self.mode = app_mode[data[0]]

        self.port_in, \
        self.port_out, \
        self.port_out_live = struct.unpack("<HHH", bytearray(data[1:]))

        self.tablero = TableroStatus(port_in=self.port_in, port_out_live=self.port_out_live)

        self.valid = True


@dataclass
class ReadSchedule(MetadataBase):
    port_out: int = 0
    schedule: List[int] = field(default_factory=list)

    def __post_init__(self, data):
        if len(data) < 2:
            self.valid = False
            return

        self.port_out = struct.unpack("<H", bytearray(data[:2]))[0]

        if len(data) < 3:
            self.valid = True
            return

        if len(data[2:]) % 4 != 0:
            self.valid = False
            return

        self.schedule = data[2:]

        self.valid = True