#!/usr/bin/python3.7
import struct, datetime

from bsp.v1.aireador import errors
from bsp.v1._generic.interfaces import MetadataBase, Command, DataReceivedBase, \
    CommandBase, ParameterBase, AddressBase, VersionBase
from bsp.v1._generic import utils

from typing import List, Union, Type
from dataclasses import dataclass, field


class Commands:
    read_schedule: Command = Command("READ_SCHEDULE", 0x16)
    run_timer_mode: Command = Command("RUN_TIMER_MODE", 0x18)
    run_standalone_mode: Command = Command("RUN_STANDALONE_MODE", 0x1A)
    run_oxygen_mode: Command = Command("RUN_OXYGEN_MODE", 0x1C)
    set_capacitor: Command = Command("SET_CAPACITOR", 0x1E)


@dataclass
class DataReceived(DataReceivedBase):

    # dictionary variables
    node_date: datetime.datetime = field(init=False)
    temperature: float = field(init=False)
    humidity: float = field(init=False)

    def __post_init__(self,
                      stream: List[int],
                      address: AddressBase,
                      version_p: VersionBase,
                      command_p: CommandBase,
                      parameter_p: ParameterBase,
                      metadata_dc: Union[Type[MetadataBase], MetadataBase]):

        super().__post_init__(stream=stream,
                              address=address,
                              version_p=version_p,
                              command_p=command_p,
                              parameter_p=parameter_p,
                              metadata_dc=metadata_dc)

        if self.status != utils.OK:
            return

        # ----------------------------------------
        # collect header and command
        if len(stream) < 16:
            self.status = utils.ERROR_DATA_LENGTH_RECEIVED
            return

        temperature_raw, \
        humidity_raw, \
        timestamp, \
        cmd_code = struct.unpack("<BBLB", bytearray(stream[4:11]))

        self.temperature = temperature_raw / 2
        self.humidity = humidity_raw / 2
        self.node_date = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc).astimezone()
        self.data = stream[11:-5]

        # ----------------------------------------
        # check command
        if cmd_code != command_p.code and cmd_code + 1 > len(errors.errors_received):
            self.status = utils.ERROR_UNKNOWN_RECEIVED_COMMAND
            return

        if cmd_code + 1 <= len(errors.errors_received):
            if not (cmd_code == 6 and len(self.data) == 4 and parameter_p.execution_id > 0):
                self.command = errors.errors_received[cmd_code]
                self.status = self.command.name
                return

            device_execution_id = struct.unpack("<L", bytearray(self.data))[0]
            if parameter_p.execution_id != device_execution_id:
                self.command = errors.errors_received[cmd_code]
                self.status = self.command.name
                return

        self.command = command_p
        self.status = utils.OK

        # ----------------------------------------
        # collect header and command
        self.metadata = metadata_dc(self.data)

        if not self.metadata.valid:
            self.status = utils.ERROR_METADATA_RECEIVED_EMPTY
