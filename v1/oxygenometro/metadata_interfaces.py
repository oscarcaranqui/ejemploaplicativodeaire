#!/usr/bin/python3.7
import datetime, struct

from bsp.v1._generic.interfaces import MetadataBase

from typing import List
from dataclasses import dataclass, field, InitVar


@dataclass
class ReadStatus(MetadataBase):
    mode: str = field(init=False)
    app_status: str = field(init=False)
    modbus_status: str = field(init=False)
    storage_status: str = field(init=False)

    device_date: datetime.datetime = field(init=False)

    def __post_init__(self, data: List[int]):
        if len(data) != 5:
            self.valid = False
            return

        app_mode = [
            "idle",
            "standalone",
            "oxygen"
        ]

        app_state = [
            "stop",
            "run"
        ]

        modbus_state = [
            "ok",
            "error"
        ]

        storage_state = [
            "empty",
            "used"
        ]

        self.mode = app_mode[3 & data[0]]
        self.app_status = app_state[1 & (data[0]>>2)]
        self.modbus_status = modbus_state[1 & (data[0]>>3)]
        self.storage_status = storage_state[1 & (data[0] >> 4)]

        try:
            timestamp = struct.unpack("<L", bytearray(data[1:5]))[0]
            self.device_date = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc).astimezone()
        except Exception as e:
            self.valid = False
            return

        self.valid = True


@dataclass
class Sample:
    stream_lst: InitVar[List[int]]

    date: datetime.datetime = field(init=False)

    dissolve_oxygen_concentration: float = field(init=False)
    doc_dqid: int = field(init=False)

    temperature: float = field(init=False)
    temp_dqid: int = field(init=False)

    dissolve_oxygen_saturation: float = field(init=False)
    dos_dqid: int = field(init=False)

    oxygen_partial_pressure: float = field(init=False)
    opp_dqid: int = field(init=False)

    internal_temperature: float = field(init=False)
    internal_humidity: float = field(init=False)

    valid: bool = field(repr=False, init=False)

    def __post_init__(self, stream_lst: List[int]):
        if len(stream_lst) != 26:
            self.valid = False
            return

        try:
            timestamp = struct.unpack("<L", bytearray(stream_lst[:4]))[0]
            self.date = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc).astimezone()
        except Exception as e:
            self.valid = False
            return

        self.dissolve_oxygen_concentration, \
        self.doc_dqid, \
        self.temperature, \
        self.temp_dqid, \
        self.dissolve_oxygen_saturation, \
        self.dos_dqid, \
        self.oxygen_partial_pressure, \
        self.opp_dqid, \
        internal_temperature_raw, \
        internal_humidity_raw = struct.unpack(">fBfBfBfBBB", bytearray(stream_lst[4:]))

        self.internal_temperature = internal_temperature_raw / 2
        self.internal_humidity = internal_humidity_raw / 2

        self.valid = True


@dataclass
class ReadSamples(ReadStatus):
    salinity: float = field(init=False)
    samples: List[Sample] = field(init=False, default_factory=list)

    def __post_init__(self, data: List[int]):
        if len(data) < 5:
            self.valid = False
            return

        super().__post_init__(data=data[:5])

        if len(data) < 9:
            self.valid = True
            return

        self.salinity = struct.unpack(">f", bytearray(data[5:9]))[0]

        sub_data = data[9:]

        if len(sub_data) % 26 != 0:
            self.valid = False
            return

        for i in range(int(len(sub_data) / 26)):
            sample = Sample(sub_data[i * 26 : (i + 1) * 26])

            if not sample.valid:
                continue

            self.samples.append(sample)

        self.valid = True
