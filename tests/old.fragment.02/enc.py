from typing import Callable

from core import arx_one, arx_two, column_func, diagonal_func, multi_xor, pht_one, pht_two


def column_collapse(data: list) -> list:
    result = []

    for col in range(4):
        column_sum = sum(data[col][row] for row in range(4))
        result.append(column_sum % pow(2, 32))

    return result


def function_sqh(data: list, key0: list, key1: list) -> list:
    def sqh(x: int, y: int, z: int) -> int:
        return (pow((x + y + z) % pow(2, 32), 2) % pow(2, 32) + 1) % pow(2, 32)

    data = [sqh(x=data[num], y=key0[num], z=key1[num]) for num in range(4)]

    inner_result = arx_one(data=data)
    outer_result = arx_two(data=inner_result)

    return outer_result


def function_f(
    data: list, key0: list, key1: list, inner_arx: Callable, outer_arx: Callable
) -> list:
    vec3 = multi_xor(data0=data, data1=key0)

    round_state = [
        data,
        key0,
        key1,
        vec3,
    ]

    inner_result = column_func(function=inner_arx, data=round_state)
    outer_result = diagonal_func(function=outer_arx, data=inner_result)
    cc_result = column_collapse(data=outer_result)
    final_vector = pht_one(data=cc_result)

    return final_vector


def encryption_gfn(d0: list, d1: list, round_keys: list) -> list:
    # sqh 1.
    res_sqh0 = function_sqh(data=d0, key0=round_keys[0][0], key1=round_keys[0][1])
    r0 = multi_xor(data0=res_sqh0, data1=d1)

    # f-1.
    res_ff1 = function_f(
        data=r0,
        key0=round_keys[1][0],
        key1=round_keys[1][1],
        inner_arx=arx_one,
        outer_arx=arx_one,
    )
    r1 = multi_xor(data0=res_ff1, data1=d0)

    # f-2.
    res_ff2 = function_f(
        data=r1,
        key0=round_keys[2][0],
        key1=round_keys[2][1],
        inner_arx=arx_one,
        outer_arx=arx_two,
    )
    r2 = multi_xor(data0=res_ff2, data1=r0)

    # f-3.
    res_ff3 = function_f(
        data=r2,
        key0=round_keys[3][0],
        key1=round_keys[3][1],
        inner_arx=arx_two,
        outer_arx=arx_one,
    )
    r3 = multi_xor(data0=res_ff3, data1=r1)

    # f-4.
    res_ff4 = function_f(
        data=r3,
        key0=round_keys[4][0],
        key1=round_keys[4][1],
        inner_arx=arx_two,
        outer_arx=arx_two,
    )
    r4 = multi_xor(data0=res_ff4, data1=r2)

    # sqh 2.
    res_sqh1 = function_sqh(data=r4, key0=round_keys[5][0], key1=round_keys[5][1])
    r5 = multi_xor(data0=res_sqh1, data1=r3)

    return r5 + r4


def encipher(d0: list, d1: list, round_keys: list) -> list:
    for num in range(4):
        gfn_result = encryption_gfn(d0=d0, d1=d1, round_keys=round_keys[num])

        fin_result = pht_two(data=gfn_result) if num < 3 else gfn_result

        d0, d1 = fin_result[:4], fin_result[4:]

    return [d0, d1]
