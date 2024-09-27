#!/usr/bin/python3.7
import crcmod

from typing import List

def transform_to_little_endian(response_big_endian: List[int]) -> List[int]:
    response_little_endian = []
    for i in range(0, len(response_big_endian), 4):
        if i + 3 >= len(response_big_endian):
            break

        response_little_endian.append(response_big_endian[i + 3])
        response_little_endian.append(response_big_endian[i + 2])
        response_little_endian.append(response_big_endian[i + 1])
        response_little_endian.append(response_big_endian[i])

    if len(response_big_endian) % 4 != 0:
        add = [0] * (4 - (len(response_big_endian) % 4))
        tmp = response_big_endian[int(len(response_big_endian) / 4) * 4:] + add

        response_little_endian.append(tmp[3])
        response_little_endian.append(tmp[2])
        response_little_endian.append(tmp[1])
        response_little_endian.append(tmp[0])

    return response_little_endian

def calculate_crc(data: List[int]) -> int:
    crc32_func = crcmod.mkCrcFun(0x104c11db7, rev=False, initCrc=0xFFFFFFFF, xorOut=0x00000000)
    data = transform_to_little_endian(data)
    return crc32_func(bytearray(data))