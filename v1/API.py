#!/usr/bin/python3.7
import datetime, pprint, json
from typing import List

from _common.utils import asdict_without_datetostr as asdict

from _common.E22_UART import E22_UART

from bsp.v1.Process import Process
from bsp.v1.Process import GatewayResponse

from bsp.v1.aireador import interfaces as AireadorInterfaces, parameter_interfaces as AireadorParameterInterfaces
from bsp.v1.aireador import metadata_interfaces as AireadorMetadataInterfaces

from bsp.v1.oxygenometro import parameter_interfaces as OxigenometroParameterInterfaces, \
    interfaces as OxigenometroInterfaces, metadata_interfaces as OxigenometroMetadataInterfaces

from bsp.v1._generic import parameter_interfaces as GenericParameterInterfaces, interfaces as GenericInterfaces


def _print_response(show: bool, gateway_response: GatewayResponse):
    def fnc(o):
        if isinstance(o, (datetime.date, datetime.datetime)):
            return str(o)

    if show:
        pprint.pprint(json.loads(json.dumps(asdict(gateway_response), default=fnc)), compact=True)
        print()

#######################################
# Metodos para gateway
#######################################


def gateway_restart():
    E22_UART.restart_lora_module()
    print({"status": "ok"})


#######################################
# Metodos para ambas aplicaciones
#######################################

def node_sync_time(retries: int, timeout_ms: int, show: bool, hw_id: int,
                   group: int, node: int, channel: int) -> GatewayResponse:

    gw_r = Process.send_command(
        retries=retries, timeout_ms=timeout_ms, hw_id=hw_id,
        address=GenericInterfaces.AddressBase(group=group, node=node, channel=channel),
        command=GenericInterfaces.Commands.sync_time,
        parameter=GenericParameterInterfaces.SyncTime(),
        matadata_received_dc=GenericInterfaces.MetadataBase
    )

    _print_response(show=show, gateway_response=gw_r)

    return gw_r


#######################################
# Metodos para aireadores
#######################################


def aireador_read_status(retries: int, timeout_ms: int, show: bool, hw_id: int,
                         group: int, channel: int, node: int) -> GatewayResponse:

    gw_r = Process.send_command(
        retries=retries, timeout_ms=timeout_ms, hw_id=hw_id,
        address=GenericInterfaces.AddressBase(group=group, node=node, channel=channel),
        command=GenericInterfaces.Commands.read_status,
        parameter=GenericInterfaces.ParameterBase(),
        matadata_received_dc=AireadorMetadataInterfaces.ReadStatus
    )

    _print_response(show=show, gateway_response=gw_r)

    return gw_r


def aireador_read_schedule(retries: int, timeout_ms: int, show: bool, hw_id: int,
                           group: int, channel: int,node: int) -> GatewayResponse:

    gw_r = Process.send_command(
        retries=retries, timeout_ms=timeout_ms, hw_id=hw_id,
        address=GenericInterfaces.AddressBase(group=group, node=node, channel=channel),
        command=AireadorInterfaces.Commands.read_schedule,
        parameter=GenericInterfaces.ParameterBase(),
        matadata_received_dc=AireadorMetadataInterfaces.ReadSchedule
    )

    _print_response(show=show, gateway_response=gw_r)

    return gw_r


def aireador_timer_mode(retries: int, timeout_ms: int, show: bool, hw_id: int,
                        group: int, channel: int, node: int,
                        aireadores: int,
                        capacitor: bool,
                        duracion: int) -> GatewayResponse:

    gw_r = Process.send_command(
        retries=retries, timeout_ms=timeout_ms, hw_id=hw_id,
        address=GenericInterfaces.AddressBase(group=group, node=node, channel=channel),
        command=AireadorInterfaces.Commands.run_timer_mode,
        parameter=AireadorParameterInterfaces.TimerMode(
            aireadores=aireadores,
            capacitor=capacitor,
            duracion=duracion
        ),
        matadata_received_dc=GenericInterfaces.MetadataBase
    )

    _print_response(show=show, gateway_response=gw_r)

    return gw_r


def aireador_standalone_mode(retries: int, timeout_ms: int, show: bool, hw_id: int,
                             group: int, channel: int, node: int,
                             aireadores: int,
                             capacitor: bool,
                             horarios: List[int]) -> GatewayResponse:

    gw_r = Process.send_command(
        retries=retries, timeout_ms=timeout_ms, hw_id=hw_id,
        address=GenericInterfaces.AddressBase(group=group, node=node, channel=channel),
        command=AireadorInterfaces.Commands.run_standalone_mode,
        parameter=AireadorParameterInterfaces.ScheduleMode(
            aireadores=aireadores,
            capacitor=capacitor,
            horarios=horarios
        ),
        matadata_received_dc=GenericInterfaces.MetadataBase
    )

    _print_response(show=show, gateway_response=gw_r)

    return gw_r


def aireador_oxygen_mode(retries: int, timeout_ms: int, show: bool, hw_id: int,
                         group: int, channel: int, node: int,
                         aireadores: int,
                         capacitor: bool,
                         horarios: List[int]) -> GatewayResponse:

    gw_r = Process.send_command(
        retries=retries, timeout_ms=timeout_ms, hw_id=hw_id,
        address=GenericInterfaces.AddressBase(group=group, node=node, channel=channel),
        command=AireadorInterfaces.Commands.run_oxygen_mode,
        parameter=AireadorParameterInterfaces.ScheduleMode(
            aireadores=aireadores,
            capacitor=capacitor,
            horarios=horarios
        ),
        matadata_received_dc=GenericInterfaces.MetadataBase
    )

    _print_response(show=show, gateway_response=gw_r)

    return gw_r


def aireador_stop(retries: int, timeout_ms: int, show: bool, hw_id: int,
                  group: int, node: int, channel: int) -> GatewayResponse:

    gw_r = Process.send_command(
        retries=retries, timeout_ms=timeout_ms, hw_id=hw_id,
        address=GenericInterfaces.AddressBase(group=group, node=node, channel=channel),
        command=GenericInterfaces.Commands.stop,
        parameter=GenericInterfaces.ParameterBase(),
        matadata_received_dc=GenericInterfaces.MetadataBase
    )

    _print_response(show=show, gateway_response=gw_r)

    return gw_r


def aireador_config_capacitor(retries: int, timeout_ms: int, show: bool, hw_id: int,
                              group: int, channel: int, node: int,
                              capacitor: bool) -> GatewayResponse:

    gw_r = Process.send_command(
        retries=retries, timeout_ms=timeout_ms, hw_id=hw_id,
        address=GenericInterfaces.AddressBase(group=group, node=node, channel=channel),
        command=AireadorInterfaces.Commands.set_capacitor,
        parameter=AireadorParameterInterfaces.SetCapacitor(
            capacitor=capacitor
        ),
        matadata_received_dc=GenericInterfaces.MetadataBase
    )

    _print_response(show=show, gateway_response=gw_r)

    return gw_r


def aireador_config_bootloader(retries: int, timeout_ms: int, show: bool, hw_id: int,
                               group: int, node: int, channel: int) -> GatewayResponse:

    gw_r = Process.send_command(
        retries=retries, timeout_ms=timeout_ms, hw_id=hw_id,
        address=GenericInterfaces.AddressBase(group=group, node=node, channel=channel),
        command=GenericInterfaces.Commands.config_boot,
        parameter=GenericInterfaces.ParameterBase(),
        matadata_received_dc=GenericInterfaces.MetadataBase
    )

    _print_response(show=show, gateway_response=gw_r)

    return gw_r


#######################################
# Metodos para oxigenometros
#######################################


def oxigenometro_read_status(retries: int, timeout_ms: int, show: bool, hw_id: int,
                             group: int, node: int, channel: int) -> GatewayResponse:

    gw_r = Process.send_command(
        retries=retries, timeout_ms=timeout_ms, hw_id=hw_id,
        address=GenericInterfaces.AddressBase(group=group, node=node, channel=channel),
        command=GenericInterfaces.Commands.read_status,
        parameter=GenericInterfaces.ParameterBase(),
        matadata_received_dc=OxigenometroMetadataInterfaces.ReadStatus
    )

    _print_response(show=show, gateway_response=gw_r)

    return gw_r


def oxigenometro_standalone_mode(retries: int, timeout_ms: int, show: bool, hw_id: int,
                                 group: int, node: int, channel: int,
                                 sampling_time: int,
                                 samples_to_reset: int,
                                 salinidad: float) -> GatewayResponse:

    gw_r = Process.send_command(
        retries=retries, timeout_ms=timeout_ms, hw_id=hw_id,
        address=GenericInterfaces.AddressBase(group=group, node=node, channel=channel),
        command=OxigenometroInterfaces.Commands.standalone_mode,
        parameter=OxigenometroParameterInterfaces.StandaloneMode(
            sampling_time=sampling_time,
            samples_to_reset=samples_to_reset,
            salinidad=salinidad
        ),
        matadata_received_dc=GenericInterfaces.MetadataBase
    )

    _print_response(show=show, gateway_response=gw_r)

    return gw_r


def oxigenometro_oxygen_mode(retries: int, timeout_ms: int, show: bool, hw_id: int,
                             group: int, node:int, channel: int,
                             sampling_time: int,
                             samples_to_reset: int,
                             salinidad: float,
                             threshold_high: float,
                             threshold_low: float,
                             slaves: int) -> GatewayResponse:

    gw_r = Process.send_command(
        retries=retries, timeout_ms=timeout_ms, hw_id=hw_id,
        address=GenericInterfaces.AddressBase(group=group, node=node, channel=channel),
        command=OxigenometroInterfaces.Commands.oxygen_mode,
        parameter=OxigenometroParameterInterfaces.OxygenMode(
            sampling_time=sampling_time,
            samples_to_reset=samples_to_reset,
            salinidad=salinidad,
            threshold_high=threshold_high,
            threshold_low=threshold_low,
            slaves=slaves
        ),
        matadata_received_dc=GenericInterfaces.MetadataBase
    )

    _print_response(show=show, gateway_response=gw_r)

    return gw_r


def oxigenometro_stop(retries: int, timeout_ms: int, show: bool, hw_id: int,
                      group: int, node: int, channel: int) -> GatewayResponse:

    gw_r = Process.send_command(
        retries=retries, timeout_ms=timeout_ms, hw_id=hw_id,
        address=GenericInterfaces.AddressBase(group=group, node=node, channel=channel),
        command=GenericInterfaces.Commands.stop,
        parameter=GenericInterfaces.ParameterBase(),
        matadata_received_dc=GenericInterfaces.MetadataBase
    )

    _print_response(show=show, gateway_response=gw_r)

    return gw_r


def oxigenometro_get_samples(retries: int, timeout_ms: int, show: bool, hw_id: int,
                             group: int, node: int, channel: int,
                             date: datetime) -> GatewayResponse:

    gw_r = Process.send_command(
        retries=retries, timeout_ms=timeout_ms, hw_id=hw_id,
        address=GenericInterfaces.AddressBase(group=group, node=node, channel=channel),
        command=OxigenometroInterfaces.Commands.read_samples,
        parameter=OxigenometroParameterInterfaces.SamplesFrom(
            date=date
        ),
        matadata_received_dc=OxigenometroMetadataInterfaces.ReadSamples
    )

    _print_response(show=show, gateway_response=gw_r)

    return gw_r


def oxigenometro_config_bootloader(retries: int, timeout_ms: int, show: bool, hw_id: int,
                                   group: int, node: int, channel: int) -> GatewayResponse:

    gw_r = Process.send_command(
        retries=retries, timeout_ms=timeout_ms, hw_id=hw_id,
        address=GenericInterfaces.AddressBase(group=group, node=node, channel=channel),
        command=GenericInterfaces.Commands.config_boot,
        parameter=GenericInterfaces.ParameterBase(),
        matadata_received_dc=GenericInterfaces.MetadataBase
    )

    _print_response(show=show, gateway_response=gw_r)

    return gw_r
