#!/usr/bin/python3.7
import time, pprint, json, datetime

from typing import Type, Union
from dataclasses import dataclass, field

from _common.E22_UART import E22_UART
from _common.Config import Config

from bsp.v1.aireador import interfaces as AireadorInterfaces
from bsp.v1.oxygenometro import interfaces as OxigenometroInterfaces

from bsp.v1._generic import utils
from bsp.v1._generic.interfaces import Command, Status, AddressBase, DataSendBase, DataReceivedBase, \
    MetadataBase, ParameterBase, VersionBase


@dataclass
class GatewayResponse:
    address: AddressBase = field(default_factory=dict)
    status: Status = field(default_factory=dict)
    data_sent: DataSendBase = field(default_factory=dict)
    data_received: DataReceivedBase = field(default_factory=dict)

    def is_response_ok(self):
        return self.status.base_station == "OK" and self.status.node == "OK"


class Process():
    AireadorBlackVersion = VersionBase(FW=1, HW=3)
    AireadorWhiteVersion = VersionBase(FW=1, HW=2)
    SotVersion = VersionBase(FW=1, HW=1)

    @staticmethod
    def _get_version(hw_id: int) -> Union[VersionBase, None]:
        if Process.AireadorBlackVersion.HW == hw_id:
            return Process.AireadorBlackVersion

        if Process.AireadorWhiteVersion.HW == hw_id:
            return Process.AireadorWhiteVersion

        if Process.SotVersion.HW == hw_id:
            return Process.SotVersion

        return None

    @staticmethod
    def _check_addh_channel(address: AddressBase) -> bool:
        serial_o = E22_UART.set_mode_command_settings()

        retry = 4
        while retry > 0:
            retry -= 1

            parameters = E22_UART.get_operating_parameters(serial_o)

            if Config.debug_lora_parameters:
                print("Loading lora, parameters: " + '[{}]'.format(', '.join(hex(x) for x in parameters)))

            if len(parameters) != 12:
                time.sleep(2)
                continue

            e22_reg = parameters[3:]

            if Config.debug_lora_parameters:
                E22_UART.print(e22_reg)

            # getting channel
            my_channel = e22_reg[E22_UART.E22_REG_OFFSET_REG2]

            # getting address
            my_addh = e22_reg[E22_UART.E22_REG_OFFSET_ADDH]
            my_addl = e22_reg[E22_UART.E22_REG_OFFSET_ADDL]

            bs_add = address.get_base_station_address_channel()

            if my_addh == bs_add[0] and my_addl == bs_add[1] and my_channel == bs_add[2]:
                serial_o.close()
                return True

            # buffer with rssi information 0xD3
            buffer = [bs_add[0], bs_add[1], 0x00, 0xe2, 0x00, bs_add[2], 0xD3, 0x01, 0x01]
            if not E22_UART.write_registers(serial_o, 0x00, 9, buffer, save_option=False):
                serial_o.close()
                time.sleep(3)
                continue

            serial_o.close()
            return True

        serial_o.close()
        return False

    @staticmethod
    def send_command(
            retries: int,
            timeout_ms: int,
            hw_id: int,
            address: AddressBase,
            command: Command,
            parameter: ParameterBase,
            matadata_received_dc: Union[Type[MetadataBase], MetadataBase]
    ) -> GatewayResponse:

        #------------------------------------------
        # check address
        if not address.valid:
            status = Status(base_station=utils.ERROR_INVALID_LORA_ADDRESS)
            gw_r = GatewayResponse(address=address, status=status)
            return gw_r

        #------------------------------------------
        # check parameters
        if not parameter.valid:
            status = Status(base_station=utils.ERROR_WRONG_PARAMETERS)
            gw_r = GatewayResponse(address=address, status=status)
            return gw_r

        #------------------------------------------
        # creating data send package
        version = Process._get_version(hw_id)
        if not version:
            status = Status(base_station=utils.ERROR_INVALID_HW_ID)
            gw_r = GatewayResponse(address=address, status=status)
            return gw_r


        data_send = DataSendBase(
            address=address,
            version=version,
            command=command.command_send,
            parameter=parameter
        )

        #-------------------------------------------
        # reconfigure base station to get local addres of group
        if not Process._check_addh_channel(address):
            status = Status(base_station=utils.ERROR_LORA_BASE_STATION)
            gw_r = GatewayResponse(address=address, status=status, data_sent=data_send)
            return gw_r

        # -------------------------------------------
        # prepare to comunicate
        serial_o = E22_UART.set_mode_transparent_transmition()

        retry = retries
        while retry > 0:
            raw = data_send.get_raw()

            if len(raw) > 240:
                status = Status(base_station=utils.ERROR_BUFFER_TX_OVERFLOW)
                gw_r = GatewayResponse(address=address, status=status, data_sent=data_send)
                return gw_r

            E22_UART.safe_send(serial_o, raw)
            response = E22_UART.receive_data(serial_o, timeout_ms)

            if not response:
                retry -= 1
                if retry == 0:
                    serial_o.close()
                    status = Status(base_station=utils.ERROR_LORA_NETWORK, attempts=(retries - retry))
                    gw_r = GatewayResponse(address=address, status=status, data_sent=data_send)
                    return gw_r
                continue

            # ------------------------------------------
            # creating data receive package
            if version == Process.AireadorWhiteVersion or version == Process.AireadorBlackVersion:
                data_received = AireadorInterfaces.DataReceived(stream=response,
                                                                address=address,
                                                                version_p=version,
                                                                command_p=command.command_received,
                                                                parameter_p=parameter,
                                                                metadata_dc=matadata_received_dc)
            else:
                data_received = OxigenometroInterfaces.DataReceived(stream=response,
                                                                    address=address,
                                                                    version_p=version,
                                                                    command_p=command.command_received,
                                                                    parameter_p=parameter,
                                                                    metadata_dc=matadata_received_dc)



            if data_received.status == utils.ERROR_CRC_RECEIVED:
                retry -= 1
                if retry == 0:
                    serial_o.close()
                    status = Status(base_station=utils.ERROR_CRC_RECEIVED, attempts=(retries - retry))
                    gw_r = GatewayResponse(address=address, status=status, data_sent=data_send)
                    return gw_r
                continue

            status = Status(base_station=utils.OK, node=data_received.status, attempts=(retries - retry))

            serial_o.close()

            gw_r = GatewayResponse(address=address, status=status, data_sent=data_send, data_received=data_received)
            return gw_r
