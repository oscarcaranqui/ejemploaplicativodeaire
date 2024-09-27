#!/usr/bin/python3.7
from bsp.v1._generic.interfaces import CommandBase

errors_received = [
    CommandBase("ERROR_CRC", 0),
    CommandBase("ERROR_UNKNOWN_CMD", 1),
    CommandBase("ERROR_INCOMPATIBLE_FW_VERSION", 2),
    CommandBase("ERROR_INCOMPATIBLE_HW_ID", 3),

    CommandBase("ERROR_SIZE_PARAMETERS", 4),
    CommandBase("ERROR_WRONG_PARAMETERS", 5),
    CommandBase("ERROR_APP_RUNNING", 6),

    CommandBase("ERROR_APP_NOT_OXYGEN_MODE", 7),
    CommandBase("ERROR_DEVICE_ADD_IS_MASTER", 8)
]