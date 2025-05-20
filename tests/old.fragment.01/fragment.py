import secrets
from typing import Any, Callable

import numpy

BYTE_LENGTH = 32
CONTAINER_SIZE = 4

CONSTANTS_A32 = (
    0x2211B809,
    0xF2C05D7A,
    0x885CC469,
    0xE2B6CBF4,
)

CONSTANTS_B32 = (
    0xE0DC4BDC,
    0xB1B09C51,
    0xB12D6D4A,
    0x607B5E8B,
)

CONSTANTS_C32 = (
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

MATRIX_MULT_A = (
    (2, 1, 1, 3),
    (3, 2, 1, 1),
    (1, 3, 2, 1),
    (1, 1, 3, 2),
)

MATRIX_MULT_B = (
    (1, 1, 3, 2),
    (2, 1, 1, 3),
    (3, 2, 1, 1),
    (1, 3, 2, 1),
)

MATRIX_MULT_C = (
    (1, 3, 2, 1),
    (1, 1, 3, 2),
    (2, 1, 1, 3),
    (3, 2, 1, 1),
)

MATRIX_MULT_D = (
    (3, 2, 1, 1),
    (1, 3, 2, 1),
    (1, 1, 3, 2),
    (2, 1, 1, 3),
)


def generate_random_bytes(size: int) -> bytes:
    return secrets.token_bytes(size)


def split_bytestring(bytestring: bytes):
    return [int.from_bytes(bytestring[i : i + 4], byteorder="big") for i in range(0, BYTE_LENGTH, 4)]


def split_into_words(container: list):
    return [container[i : i + 4] for i in range(0, len(container), 4)]


def add(x=int, y=int) -> int:
    return (x + y) % pow(2, BYTE_LENGTH)


def xor(x: int, y: int) -> int:
    return x ^ y


def lcr(x: int, shift: int) -> int:
    return (pow(2, BYTE_LENGTH) - 1) & (x << shift | x >> (BYTE_LENGTH - shift))


def multi_lcr(container: list, shifters: list) -> list:
    return [lcr(x=container[i], shift=shifters[i]) for i in range(CONTAINER_SIZE)]


def multi_xor(container_a: list, container_b: list) -> list:
    return [container_a[i] ^ container_b[i] for i in range(CONTAINER_SIZE)]


def multi_add(container_a: list, container_b: list) -> list:
    return [add(x=container_a[i], y=container_b[i]) for i in range(CONTAINER_SIZE)]


def matrix_add(container_a: list, container_b: list) -> list:
    result = []
    for i in range(CONTAINER_SIZE):
        row = []
        for j in range(CONTAINER_SIZE):
            row.append(add(x=container_a[i][j], y=container_b[i][j]))
        result.append(row)
    return result


def matrix_mult(container: list, matrix: list | tuple):
    a = numpy.array(container, dtype=numpy.uint32)
    b = numpy.array(matrix, dtype=numpy.uint32)
    result = numpy.matmul(a, b)
    return result.tolist()


def arx_one(container: list) -> list:
    container[0] ^= container[2]
    container[0] = lcr(x=container[0], shift=9)
    container[3] = add(x=container[0], y=container[3])
    container[2] ^= container[3]
    container[2] = lcr(x=container[2], shift=17)
    container[1] = add(x=container[1], y=container[2])
    container[0] ^= container[1]
    container[0] = lcr(x=container[0], shift=13)
    container[3] = add(x=container[0], y=container[3])
    container[2] ^= container[3]
    container[2] = lcr(x=container[2], shift=11)
    container[1] = add(x=container[1], y=container[2])

    return container


def arx_two(container: list) -> list:
    container[0] = add(x=container[0], y=container[2])
    container[1] ^= container[0]
    container[1] = lcr(x=container[1], shift=9)
    container[2] = add(x=container[2], y=container[1])
    container[3] ^= container[2]
    container[3] = lcr(x=container[3], shift=17)
    container[0] = add(x=container[0], y=container[3])
    container[1] ^= container[0]
    container[1] = lcr(x=container[1], shift=13)
    container[2] = add(x=container[2], y=container[1])
    container[3] ^= container[2]
    container[3] = lcr(x=container[3], shift=11)

    return container


def matrix_mult(container: list, matrix: list | tuple):
    # used numpy because i'm tired.
    a = numpy.array(container, dtype=numpy.uint32)
    b = numpy.array(matrix, dtype=numpy.uint32)
    result = numpy.matmul(a, b)
    return result.tolist()


def function_k1(container: list, constant: int) -> list:
    container[2] ^= constant
    res = arx_one(container=arx_one(container=container))
    final = matrix_mult(container=res, matrix=MATRIX_MULT_A)

    return final


def function_k2(container: list, constant: int) -> list:
    container[2] ^= constant
    res = arx_two(container=arx_one(container=container))
    final = matrix_mult(container=res, matrix=MATRIX_MULT_B)

    return final


def function_k3(container: list, constant: int) -> list:
    container[2] ^= constant
    res = arx_one(container=arx_two(container=container))
    final = matrix_mult(container=res, matrix=MATRIX_MULT_C)

    return final


def function_k4(container: list, constant: int) -> list:
    container[2] ^= constant
    res = arx_two(container=arx_two(container=container))
    final = matrix_mult(container=res, matrix=MATRIX_MULT_D)

    return final


def ksa_gfn_4r(left: list, right: list, constants: list) -> list:
    res_fk1 = function_k1(container=left, constant=constants[0])
    r0 = multi_lcr(container=right, shifters=MATRIX_MULT_D[0])
    r1 = multi_xor(container_a=res_fk1, container_b=r0)

    res_fk2 = function_k2(container=r1, constant=constants[1])
    r2 = multi_lcr(container=left, shifters=MATRIX_MULT_D[1])
    r3 = multi_xor(container_a=res_fk2, container_b=r2)

    res_fk3 = function_k3(container=r3, constant=constants[2])
    r4 = multi_lcr(container=r1, shifters=MATRIX_MULT_D[2])
    r5 = multi_xor(container_a=res_fk3, container_b=r4)

    res_fk4 = function_k4(container=r5, constant=constants[3])
    r6 = multi_lcr(container=r3, shifters=MATRIX_MULT_D[3])
    r7 = multi_xor(container_a=res_fk4, container_b=r6)

    return [r7, r5]


def column_arx(function: Callable, container: list) -> list:
    return [
        function(container=[container[0][0], container[1][0], container[2][0], container[3][0]]),
        function(container=[container[0][1], container[1][1], container[2][1], container[3][1]]),
        function(container=[container[0][2], container[1][2], container[2][2], container[3][2]]),
        function(container=[container[0][3], container[1][3], container[2][3], container[3][3]]),
    ]


def diagonal_arx(function: Callable, container: list) -> list:
    return [
        function(container=[container[0][0], container[1][1], container[2][2], container[3][3]]),
        function(container=[container[0][1], container[1][2], container[2][3], container[3][0]]),
        function(container=[container[0][2], container[1][3], container[2][0], container[3][1]]),
        function(container=[container[0][3], container[1][0], container[2][1], container[3][2]]),
    ]


def ksa(secret_key: list) -> list:
    res_ksa_4ra = ksa_gfn_4r(left=secret_key[0], right=secret_key[1], constants=CONSTANTS_A32)

    res_a_left = multi_add(container_a=secret_key[0], container_b=res_ksa_4ra[0])
    res_a_right = multi_add(container_a=secret_key[1], container_b=res_ksa_4ra[1])

    res_ksa_4rb = ksa_gfn_4r(left=res_ksa_4ra[0], right=res_ksa_4ra[1], constants=CONSTANTS_B32)

    res_b_left = multi_add(container_a=res_ksa_4ra[0], container_b=res_ksa_4rb[0])
    res_b_right = multi_add(container_a=res_ksa_4ra[1], container_b=res_ksa_4rb[1])

    round_keys: list = []

    # initialization keys
    initk = [
        res_a_left,
        res_b_left,
        res_b_right,
        res_a_right,
    ]

    for constant in CONSTANTS_C32:
        initk[0][0] ^= constant

        column = column_arx(function=arx_one, container=initk)
        diagonal = diagonal_arx(function=arx_two, container=column)

        s2 = matrix_mult(container=diagonal, matrix=MATRIX_MULT_C)
        final_round_keys = matrix_add(container_a=initk, container_b=s2)

        round_keys.append(final_round_keys[:2])
        round_keys.append(final_round_keys[2:])

        initk = s2

    return round_keys


def function_sqh(container: list, key1: list, key2: list) -> list:
    def sqh(x: int, y: int, z: int) -> int:
        return (pow((x + y + z) % pow(2, BYTE_LENGTH), 2) % pow(2, BYTE_LENGTH) + 1) % pow(2, BYTE_LENGTH)

    for num in range(CONTAINER_SIZE):
        container[num] = sqh(x=container[num], y=key1[num], z=key2[num])

    res_arx_one = arx_one(container=container)
    result = arx_two(container=res_arx_one)

    return result


def column_collapse(container: list) -> list:
    result = []

    for col in range(CONTAINER_SIZE):
        column_sum = sum(container[col][row] for row in range(CONTAINER_SIZE))
        result.append(column_sum % pow(2, BYTE_LENGTH))

    return result


def function_f1(container: list, key1: list, key2: list) -> list:
    enc_vector = [container[i] ^ key1[i] for i in range(CONTAINER_SIZE)]
    round_state = [container, key1, key2, enc_vector]

    column = column_arx(function=arx_one, container=round_state)
    diagonal = diagonal_arx(function=arx_one, container=column)

    matrix = matrix_mult(container=diagonal, matrix=MATRIX_MULT_A)
    result = column_collapse(container=matrix)

    return result


def function_f2(container: list, key1: list, key2: list) -> list:
    enc_vector = [container[i] ^ key1[i] for i in range(CONTAINER_SIZE)]
    round_state = [container, key1, key2, enc_vector]

    column = column_arx(function=arx_one, container=round_state)
    diagonal = diagonal_arx(function=arx_two, container=column)

    matrix = matrix_mult(container=diagonal, matrix=MATRIX_MULT_B)
    result = column_collapse(container=matrix)

    return result


def function_f3(container: list, key1: list, key2: list) -> list:
    enc_vector = [container[i] ^ key1[i] for i in range(CONTAINER_SIZE)]
    round_state = [container, key1, key2, enc_vector]

    column = column_arx(function=arx_two, container=round_state)
    diagonal = diagonal_arx(function=arx_one, container=column)

    matrix = matrix_mult(container=diagonal, matrix=MATRIX_MULT_C)
    result = column_collapse(container=matrix)

    return result


def function_f4(container: list, key1: list, key2: list) -> list:
    enc_vector = [container[i] ^ key1[i] for i in range(CONTAINER_SIZE)]
    round_state = [container, key1, key2, enc_vector]

    column = column_arx(function=arx_two, container=round_state)
    diagonal = diagonal_arx(function=arx_two, container=column)

    matrix = matrix_mult(container=diagonal, matrix=MATRIX_MULT_D)
    result = column_collapse(container=matrix)

    return result


def enc_gfn_6r(container: list, round_keys: list) -> list:
    res_sqh_start = function_sqh(container=container[0], key1=round_keys[0][0], key2=round_keys[0][1])
    r1 = multi_xor(container_a=res_sqh_start, container_b=container[1])

    res_f1 = function_f1(container=r1, key1=round_keys[1][0], key2=round_keys[1][1])
    r2 = multi_xor(container_a=res_f1, container_b=container[0])

    res_f2 = function_f2(container=r2, key1=round_keys[2][0], key2=round_keys[2][1])
    r3 = multi_xor(container_a=res_f2, container_b=r1)

    res_f3 = function_f3(container=r3, key1=round_keys[3][0], key2=round_keys[3][1])
    r4 = multi_xor(container_a=res_f3, container_b=r2)

    res_f4 = function_f4(container=r4, key1=round_keys[4][0], key2=round_keys[4][1])
    r5 = multi_xor(container_a=res_f4, container_b=r3)

    res_sqh_end = function_sqh(container=r5, key1=round_keys[5][0], key2=round_keys[5][1])
    r6 = multi_xor(container_a=res_sqh_end, container_b=r4)

    return [r6, r5]


def fragment_enc(iv: list, round_keys: list) -> list:
    round_key_set = (
        round_keys[0:6],
        round_keys[6:12],
        round_keys[12:18],
        round_keys[18:24],
    )

    for rks in round_key_set:
        res = enc_gfn_6r(container=iv, round_keys=rks)
        # add PHT mixer here!
        iv = res

    return iv
