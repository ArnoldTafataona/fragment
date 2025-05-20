import secrets
from typing import Callable

import numpy as np

MATRIX_00 = (
    (2, 1, 1, 3),
    (3, 2, 1, 1),
    (1, 3, 2, 1),
    (1, 1, 3, 2),
)

MATRIX_01 = (
    (1, 1, 3, 2),
    (2, 1, 1, 3),
    (3, 2, 1, 1),
    (1, 3, 2, 1),
)

MATRIX_02 = (
    (1, 3, 2, 1),
    (1, 1, 3, 2),
    (2, 1, 1, 3),
    (3, 2, 1, 1),
)

MATRIX_03 = (
    (3, 2, 1, 1),
    (1, 3, 2, 1),
    (1, 1, 3, 2),
    (2, 1, 1, 3),
)

KSA_CONSTANTS_00 = (
    0x2211B809,
    0xF2C05D7A,
    0x885CC469,
    0xE2B6CBF4,
)

KSA_CONSTANTS_01 = (
    0xE0DC4BDC,
    0xB1B09C51,
    0xB12D6D4A,
    0x607B5E8B,
)

KSA_CONSTANTS_02 = (
    0x65454984,
    0x177C5836,
    0x6C6486CC,
    0x65053BEB,
    0x0E402AA6,
    0xD5FD988F,
    0x0BBA3FBE,
    0xEE730A46,
)


def generate_random_bytes(size: int) -> bytes:
    return secrets.token_bytes(size)


def bytes_to_integers(bytestring: bytes) -> list:
    return [int.from_bytes(bytestring[i : i + 4], byteorder="big") for i in range(0, 32, 4)]


def integer_to_bytes(integers: list) -> bytes:
    return b"".join([num.to_bytes(4, byteorder="big") for num in integers]).hex()


def add(x=int, y=int) -> int:
    return (x + y) % pow(2, 32)


def multi_add(data_00: list, data_01: list) -> list:
    return [add(x=data_00[i], y=data_01[i]) for i in range(4)]


def matrix_add(data_00: list, data_01: list) -> list:
    result = []
    for i in range(4):
        row = []
        for j in range(4):
            row.append(add(x=data_00[i][j], y=data_01[i][j]))
        result.append(row)
    return result


def matrix_mult(data: list, matrix: tuple) -> list:
    m_00 = np.array(data, dtype=np.uint32)
    m_01 = np.array(matrix, dtype=np.uint32)

    result = np.dot(m_00, m_01).tolist()

    return result


def lcr(x: int, shift: int) -> int:
    return (pow(2, 32) - 1) & (x << shift | x >> (32 - shift))


def multi_lcr(data: list, shifters: list) -> list:
    return [lcr(x=data[i], shift=shifters[i]) for i in range(4)]


def multi_xor(data_00: list, data_01: list) -> list:
    return [data_00[i] ^ data_01[i] for i in range(4)]


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


def pht_4x4(data: list, iterations: int = 4) -> list:
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


#### KSA - BEGIN ####
def ksa_round_func(data: list, key: int, inner_arx: Callable, outer_arx: Callable) -> list:
    data[2] ^= key

    inner_result = inner_arx(data=data)
    outer_result = outer_arx(data=inner_result)
    final_result = pht_4x4(data=outer_result)

    return final_result


def ksa_gfn(data_00: list, data_01: list, keys: list, matrix: tuple) -> tuple:
    # round 1.
    fnc_00 = ksa_round_func(data=data_00, key=keys[0], inner_arx=arx_one, outer_arx=arx_one)
    lcr_00 = multi_lcr(data=data_01, shifters=matrix[0])
    res_00 = multi_xor(data_00=fnc_00, data_01=lcr_00)

    # round 2.
    fnc_01 = ksa_round_func(data=res_00, key=keys[1], inner_arx=arx_one, outer_arx=arx_two)
    lcr_01 = multi_lcr(data=data_00, shifters=matrix[1])
    res_01 = multi_xor(data_00=fnc_01, data_01=lcr_01)

    # round 3.
    fnc_02 = ksa_round_func(data=res_01, key=keys[2], inner_arx=arx_two, outer_arx=arx_one)
    lcr_02 = multi_lcr(data=res_00, shifters=matrix[2])
    res_02 = multi_xor(data_00=fnc_02, data_01=lcr_02)

    # round 4.
    fnc_03 = ksa_round_func(data=res_02, key=keys[3], inner_arx=arx_two, outer_arx=arx_two)
    lcr_03 = multi_lcr(data=res_01, shifters=matrix[3])
    res_03 = multi_xor(data_00=fnc_03, data_01=lcr_03)

    return res_03, res_02


def key_schedule(secret_key: bytes) -> list:
    k2i = bytes_to_integers(secret_key)
    k00 = k2i[:4]
    k01 = k2i[4:]

    r00 = ksa_gfn(data_00=k00, data_01=k01, keys=KSA_CONSTANTS_00, matrix=MATRIX_00)
    d00 = r00[0]
    d01 = r00[1]

    r01 = ksa_gfn(data_00=d00, data_01=d01, keys=KSA_CONSTANTS_01, matrix=MATRIX_03)
    d02 = r01[0]
    d03 = r01[1]

    temporary_key_matrix = (
        multi_add(data_00=k00, data_01=d00),
        multi_add(data_00=d00, data_01=d02),
        multi_add(data_00=d01, data_01=d03),
        multi_add(data_00=k01, data_01=d01),
    )

    round_keys = []

    for k in KSA_CONSTANTS_02:
        temporary_key_matrix[0][0] ^= k

        res_00 = column_func(function=arx_one, data=temporary_key_matrix)
        res_01 = diagonal_func(function=arx_two, data=res_00)

        final_key_matrix = matrix_add(data_00=temporary_key_matrix, data_01=res_01)

        round_keys.append(final_key_matrix[0])
        round_keys.append(final_key_matrix[1])
        round_keys.append(final_key_matrix[2])
        round_keys.append(final_key_matrix[3])

        temporary_key_matrix = res_01

    return round_keys


#### KSA - END ####


#### ENC - BEGIN ####
def sqh_round_func(data: list, key: list) -> list:
    def sqh(x: int, y: int) -> int:
        return (pow((x + y) % pow(2, 32), 2) % pow(2, 32) + 1) % pow(2, 32)

    sqh_result = [sqh(x=data[num], y=key[num]) for num in range(4)]
    pht_result = pht_4x4(data=sqh_result)

    return pht_result


def splitter(data: list, step_size: int) -> list:
    return [data[i : i + step_size] for i in range(0, len(data), step_size)]


def enc_round_func(
    data: list, key: list, inner_arx: Callable, outer_arx: Callable, matrix: tuple
) -> list:
    res_xor = multi_xor(data_00=data, data_01=key)
    res_inner = inner_arx(res_xor)
    res_outer = outer_arx(res_inner)
    res_mmul = matrix_mult(data=res_outer, matrix=matrix)
    res_pht = pht_4x4(data=res_mmul)

    return res_pht


def enc_round_8r_gfn(branchL: list, branchR: list, round_keys: list) -> list:
    # round 1.
    fnc_00 = enc_round_func(
        data=branchL, key=round_keys[0], inner_arx=arx_one, outer_arx=arx_one, matrix=MATRIX_00
    )
    res_00 = multi_xor(data_00=fnc_00, data_01=branchR)

    # round 2.
    fnc_01 = enc_round_func(
        data=res_00, key=round_keys[1], inner_arx=arx_two, outer_arx=arx_two, matrix=MATRIX_03
    )
    res_01 = multi_xor(data_00=fnc_01, data_01=branchL)

    # round 3.
    fnc_02 = enc_round_func(
        data=res_01, key=round_keys[2], inner_arx=arx_one, outer_arx=arx_two, matrix=MATRIX_01
    )
    res_02 = multi_xor(data_00=fnc_02, data_01=res_00)

    # round 4.
    fnc_03 = enc_round_func(
        data=res_02, key=round_keys[3], inner_arx=arx_two, outer_arx=arx_one, matrix=MATRIX_02
    )
    res_03 = multi_xor(data_00=fnc_03, data_01=res_01)

    # round 5.
    fnc_04 = enc_round_func(
        data=res_03, key=round_keys[4], inner_arx=arx_two, outer_arx=arx_one, matrix=MATRIX_02
    )
    res_04 = multi_xor(data_00=fnc_04, data_01=res_02)

    # round 6.
    fnc_05 = enc_round_func(
        data=res_04, key=round_keys[5], inner_arx=arx_one, outer_arx=arx_two, matrix=MATRIX_01
    )
    res_05 = multi_xor(data_00=fnc_05, data_01=res_03)

    # round 7.
    fnc_06 = enc_round_func(
        data=res_05, key=round_keys[6], inner_arx=arx_two, outer_arx=arx_two, matrix=MATRIX_03
    )
    res_06 = multi_xor(data_00=fnc_06, data_01=res_04)

    # round 8.
    fnc_07 = enc_round_func(
        data=res_06, key=round_keys[7], inner_arx=arx_one, outer_arx=arx_one, matrix=MATRIX_00
    )
    res_07 = multi_xor(data_00=fnc_07, data_01=res_05)

    return res_07, res_06


def encrypt(data: list, round_keys: list) -> list:
    branchL = data[:4]
    branchR = data[4:]

    round_keys = splitter(data=round_keys, step_size=8)

    for keys in round_keys:
        branchL, branchR = enc_round_8r_gfn(branchL=branchL, branchR=branchR, round_keys=keys)

    return branchR + branchL


def decrypt(data: list, round_keys: list) -> list:
    round_keys.reverse()

    result = encrypt(data=data, round_keys=round_keys)

    return result


#### ENC - END ####
