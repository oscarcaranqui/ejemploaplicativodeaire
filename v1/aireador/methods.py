#!/usr/bin/python3.7

def capacitor_to_port_out(salidas: int, capacitor: bool) -> int:
    port_out = ((2 ** salidas) - 1)
    if capacitor: port_out &= 0x0F
    else: port_out |= 0x10

    return port_out