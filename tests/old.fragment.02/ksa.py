from typing import Callable

from core import (
    arx_one,
    arx_two,
    column_func,
    diagonal_func,
    matrix_add,
    multi_add,
    multi_lcr,
    multi_xor,
    pht_one,
)

KSA_CONSTANTS_A = (
    0x2211B809,
    0xF2C05D7A,
    0x885CC469,
    0xE2B6CBF4,
)

KSA_CONSTANTS_B = (
    0xE0DC4BDC,
    0xB1B09C51,
    0xB12D6D4A,
    0x607B5E8B,
)

KSA_CONSTANTS_C = (
    0x4E45C191,
    0xBB6433B7,
    0x0B5D4207,
    0x2D4AB170,
    0x54841E88,
    0x117DE3FB,
    0x2030C3B7,
    0xD9518060,
    0x9A7D7CEB,
    0xE6AAA45B,
    0xFEDF0AC7,
    0x8D3A446E,
)

MATRIX = (
    (3, 2, 1, 1),
    (1, 3, 2, 1),
    (1, 1, 3, 2),
    (2, 1, 1, 3),
)


def function_k(data: list, constant: int, inner_arx: Callable, outer_arx: Callable) -> list:
    data[2] ^= constant

    inner_result = inner_arx(data=data)
    outer_result = outer_arx(data=inner_result)
    final_result = pht_one(data=outer_result)

    return final_result


def key_schedule_gfn(k0: list, k1: list, constants: tuple) -> list:
    res_fk1 = function_k(
        data=k0,
        constant=constants[0],
        inner_arx=arx_one,
        outer_arx=arx_one,
    )
    r0 = multi_lcr(data=k1, shifters=MATRIX[0])
    r1 = multi_xor(data0=res_fk1, data1=r0)

    res_fk2 = function_k(
        data=r1,
        constant=constants[1],
        inner_arx=arx_one,
        outer_arx=arx_two,
    )
    r2 = multi_lcr(data=k0, shifters=MATRIX[1])
    r3 = multi_xor(data0=res_fk2, data1=r2)

    res_fk3 = function_k(
        data=r3,
        constant=constants[2],
        inner_arx=arx_two,
        outer_arx=arx_one,
    )
    r4 = multi_lcr(data=r1, shifters=MATRIX[2])
    r5 = multi_xor(data0=res_fk3, data1=r4)

    res_fk4 = function_k(
        data=r5,
        constant=constants[3],
        inner_arx=arx_two,
        outer_arx=arx_two,
    )
    r6 = multi_lcr(data=r3, shifters=MATRIX[3])
    r7 = multi_xor(data0=res_fk4, data1=r6)

    return [r7, r5]


def key_schedule(key: list) -> list:
    k0: list = key[:4]
    k1: list = key[4:]

    kda_first = key_schedule_gfn(k0=k0, k1=k1, constants=KSA_CONSTANTS_A)
    kda_last = key_schedule_gfn(k0=kda_first[0], k1=kda_first[1], constants=KSA_CONSTANTS_B)

    temp_key_matrix = [
        multi_add(data0=k0, data1=kda_first[0]),
        multi_add(data0=kda_first[0], data1=kda_last[0]),
        multi_add(data0=kda_first[1], data1=kda_last[1]),
        multi_add(data0=k1, data1=kda_first[1]),
    ]

    round_keys: list = []

    for constant in KSA_CONSTANTS_C:
        temp_key_matrix[0][0] ^= constant

        res_c0 = column_func(function=arx_one, data=temp_key_matrix)
        res_d0 = diagonal_func(function=arx_two, data=res_c0)

        final_key_matrix = matrix_add(data0=temp_key_matrix, data1=res_d0)

        round_keys.append(final_key_matrix[:2])
        round_keys.append(final_key_matrix[2:])

        temp_key_matrix = res_d0

    return round_keys
