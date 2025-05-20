import secrets
from typing import Callable


def generate_random_bytes(size: int) -> bytes:
    return secrets.token_bytes(size)


def bytes_to_integers(bytestring: bytes) -> list:
    return [int.from_bytes(bytestring[i : i + 4], byteorder="big") for i in range(0, 32, 4)]


def add(x=int, y=int) -> int:
    return (x + y) % pow(2, 32)


def multi_add(data0: list, data1: list) -> list:
    return [add(x=data0[i], y=data1[i]) for i in range(4)]


def matrix_add(data0: list, data1: list) -> list:
    result = []
    for i in range(4):
        row = []
        for j in range(4):
            row.append(add(x=data0[i][j], y=data1[i][j]))
        result.append(row)
    return result


def lcr(x: int, shift: int) -> int:
    return (pow(2, 32) - 1) & (x << shift | x >> (32 - shift))


def multi_lcr(data: list, shifters: list) -> list:
    return [lcr(x=data[i], shift=shifters[i]) for i in range(4)]


def multi_xor(data0: list, data1: list) -> list:
    return [data0[i] ^ data1[i] for i in range(4)]


def arx_one(data: list) -> list:
    data[0] ^= data[2]
    data[0] = lcr(x=data[0], shift=9)
    data[3] = add(x=data[0], y=data[3])
    data[2] ^= data[3]
    data[2] = lcr(x=data[2], shift=17)
    data[1] = add(x=data[1], y=data[2])
    data[0] ^= data[1]
    data[0] = lcr(x=data[0], shift=13)
    data[3] = add(x=data[0], y=data[3])
    data[2] ^= data[3]
    data[2] = lcr(x=data[2], shift=11)
    data[1] = add(x=data[1], y=data[2])

    return data


def arx_two(data: list) -> list:
    data[0] = add(x=data[0], y=data[2])
    data[1] ^= data[0]
    data[1] = lcr(x=data[1], shift=9)
    data[2] = add(x=data[2], y=data[1])
    data[3] ^= data[2]
    data[3] = lcr(x=data[3], shift=17)
    data[0] = add(x=data[0], y=data[3])
    data[1] ^= data[0]
    data[1] = lcr(x=data[1], shift=13)
    data[2] = add(x=data[2], y=data[1])
    data[3] ^= data[2]
    data[3] = lcr(x=data[3], shift=11)

    return data


def column_func(function: Callable, data: list) -> list:
    return [
        function(data=[data[0][0], data[1][0], data[2][0], data[3][0]]),
        function(data=[data[0][1], data[1][1], data[2][1], data[3][1]]),
        function(data=[data[0][2], data[1][2], data[2][2], data[3][2]]),
        function(data=[data[0][3], data[1][3], data[2][3], data[3][3]]),
    ]


def diagonal_func(function: Callable, data: list) -> list:
    return [
        function(data=[data[0][0], data[1][1], data[2][2], data[3][3]]),
        function(data=[data[0][1], data[1][2], data[2][3], data[3][0]]),
        function(data=[data[0][2], data[1][3], data[2][0], data[3][1]]),
        function(data=[data[0][3], data[1][0], data[2][1], data[3][2]]),
    ]


def pht_one(data: list, iterations: int = 4) -> list:
    for _ in range(iterations):
        data[0] = add(x=data[0], y=data[1])
        data[1] = add(x=data[1], y=(2 * data[0]))
        data[2] = add(x=data[2], y=data[3])
        data[3] = add(x=data[3], y=(2 * data[2]))

        data = [
            data[1],
            data[2],
            data[3],
            data[0],
        ]

    return data


def pht_two(data: list, iterations: int = 8) -> list:
    for _ in range(iterations):
        data[0] = add(x=data[0], y=data[1])
        data[1] = add(x=data[1], y=(2 * data[0]))
        data[2] = add(x=data[2], y=data[3])
        data[3] = add(x=data[3], y=(2 * data[2]))
        data[4] = add(x=data[4], y=data[5])
        data[5] = add(x=data[5], y=(2 * data[4]))
        data[6] = add(x=data[6], y=data[7])
        data[7] = add(x=data[7], y=(2 * data[6]))

        data = [
            data[1],
            data[2],
            data[3],
            data[4],
            data[5],
            data[6],
            data[7],
            data[0],
        ]

    return data
