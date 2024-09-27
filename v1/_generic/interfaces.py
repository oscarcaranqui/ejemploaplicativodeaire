#!/usr/bin/python3.7
import datetime, struct

from bsp.v1._generic import methods, utils

from typing import List, Union, Type
from dataclasses import dataclass, field, InitVar


@dataclass
class Status:
    base_station: str = ""
    node: str = ""
    attempts: int = 0

    valid: bool = field(repr=False, init=False)

    def __post_init__(self):
        self.valid = (self.base_station == utils.OK and self.node == utils.OK)


@dataclass
class AddressBase:
    group: int
    node: int
    channel: int

    addh: int = field(init=False)
    addl: int = field(init=False)

    valid: bool = field(repr=False, init=False)

    def __post_init__(self):
        self.addh = 0
        self.addl = 0

        if self.group > 8190 or self.group < 1:
            self.valid = False
            return

        if self.node > 7 or self.node < 1:
            self.valid = False
            return

        self.addh = 0xFF & (self.group >> 5)
        self.addl = 0xFF & (self.group << 3) +  self.node

        if self.channel > 80 or self.channel < 0:
            self.valid = False
            return

        self.valid = True

    def get_global_address(self) -> List[int]:
        return [self.addh, self.addl]

    def get_global_address_channel(self) -> List[int]:
        return self.get_global_address() + [self.channel]

    def get_base_station_address(self) -> List[int]:
        return [self.addh, self.addl & 0xF8]

    def get_base_station_address_channel(self) -> List[int]:
        return self.get_base_station_address() + [self.channel]

@dataclass
class HWVersionDescription:
    smart_plc_white: str = "smart_plc_white"
    smart_plc_black: str = "smart_plc_black"
    smart_feeder_black: str = "smart_feeder_black"
    unknown: str = "unknown"


@dataclass
class VersionBase:
    FW: int
    HW: int
    HW_description: str = field(init=False)

    def __post_init__(self):
        self.HW_description = HWVersionDescription.unknown

        if self.HW == 1:
            self.HW_description = HWVersionDescription.smart_feeder_black

        if self.HW == 2:
            self.HW_description = HWVersionDescription.smart_plc_white

        if self.HW == 3:
            self.HW_description = HWVersionDescription.smart_plc_black

    def get_raw(self) -> List[int]:
        return [self.FW, self.HW]


@dataclass
class MetadataBase:
    data: InitVar[List[int]]
    valid: bool = field(repr=False, init=False)

    def __post_init__(self, data):
        self.valid = True


@dataclass
class ParameterBase:
    execution_id: int = field(repr=False, init=False)
    valid: bool = field(repr=False, init=False)

    def __post_init__(self):
        self.execution_id = 0
        self.valid = True

    def get_raw(self) -> List[int]:
        return []


@dataclass
class CommandBase:
    name: str
    code: int


@dataclass
class Command:
    name: InitVar[str]
    code_send: InitVar[int]

    command_send: CommandBase = field(init=False)
    command_received: CommandBase = field(init=False)

    def __post_init__(self, name, code_send):
        self.command_send = CommandBase(name=("SEND_" + name), code=code_send)
        self.command_received = CommandBase(name=("RECEIVED_" + name), code=(code_send + 1))


@dataclass
class DataSendBase:
    address: AddressBase = field(repr=False)
    valid: bool = field(repr=False, init=False)

    date: datetime.datetime = field(init=False)
    version: VersionBase
    command: CommandBase
    parameter: ParameterBase
    raw: List[int] = field(init=False)

    def __post_init__(self):
        self.date = datetime.datetime.now(tz=datetime.timezone.utc).astimezone()
        self.raw = []

    def get_raw(self) -> List[int]:
        buffer = self.version.get_raw() + \
                 self.address.get_base_station_address() + \
                 [self.command.code] + \
                 self.parameter.get_raw()

        crc = methods.calculate_crc(buffer)
        crc_lst = list(struct.pack("<L", int(crc)))

        self.raw = self.address.get_global_address_channel() + buffer + crc_lst
        return self.raw


@dataclass
class DataReceivedBase:
    stream: InitVar[List[int]]
    address: InitVar[AddressBase]
    version_p: InitVar[VersionBase]
    command_p: InitVar[CommandBase]
    parameter_p: InitVar[ParameterBase]
    metadata_dc: InitVar[Union[Type[MetadataBase], MetadataBase]]

    status: str = field(repr=False, init=False)

    date: datetime.datetime = field(init=False)
    addh: int = field(repr=False, init=False)
    addl: int = field(repr=False, init=False)
    crc: int = field(repr=False, init=False)
    data: List[int] = field(repr=False, init=False, default_factory=list)

    raw: List[int] = field(init=False)
    rssi: float = field(init=False)
    version: VersionBase = field(init=False)
    command: CommandBase = field(init=False)
    metadata: MetadataBase = field(init=False)

    def __post_init__(self,
                      stream: List[int],
                      address: AddressBase,
                      version_p: VersionBase,
                      command_p: CommandBase,
                      parameter_p: ParameterBase,
                      metadata_dc: Union[Type[MetadataBase], MetadataBase]):

        self.reception_date = datetime.datetime.now(tz=datetime.timezone.utc).astimezone()
        self.raw = stream

        # ----------------------------------------
        # check CRC of stream
        if len(stream) < 5:
            self.status = utils.ERROR_DATA_LENGTH_RECEIVED
            return

        self.crc, \
        rssi = struct.unpack("<LB", bytearray(stream[-5:]))
        crc = methods.calculate_crc(stream[:-5])

        self.rssi = - rssi / 2

        if crc != self.crc:
            self.status = utils.ERROR_CRC_RECEIVED
            return

        # ----------------------------------------
        # check Version of stream
        if len(stream) < 7:
            self.status = utils.ERROR_DATA_LENGTH_RECEIVED
            return

        fw, \
        hw = struct.unpack("BB", bytearray(stream[:2]))
        self.version = VersionBase(FW=fw, HW=hw)

        if not (self.version.FW == version_p.FW and self.version.HW == version_p.HW):
            self.status = utils.ERROR_INVALID_VERSION
            return

        # ----------------------------------------
        # check address of stream
        if len(stream) < 9:
            self.status = utils.ERROR_DATA_LENGTH_RECEIVED
            return

        self.addh, \
        self.addl = struct.unpack("BB", bytearray(stream[2:4]))

        if not (self.addh == address.addh and self.addl == address.addl):
            self.status = utils.ERROR_DATA_COMMING_FROM_OTHER_DEVICE

        self.status = utils.OK



class Commands:
    read_status: Command = Command("READ_STATUS", 0x10)
    sync_time: Command = Command("SYNC_TIME", 0x12)
    stop: Command = Command("STOP", 0x14)
    config_boot: Command = Command("SET_CONFIG_BOOT", 0xFD)

