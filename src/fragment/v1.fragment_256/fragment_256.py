"""Fragment-256 Core Functionality"""


def prepare_data(data: bytes, length: int, to_integer: bool) -> list[int]:
    if to_integer:
        return [int.from_bytes(data[x : x + length], "big") for x in range(0, len(data), length)]

    return [data[x : x + length] for x in range(0, len(data), length)]


def xor_array(data_01: list, data_02: list, length: int) -> list:
    return [data_01[x] ^ data_02[x] for x in range(length)]


def modulo_addition(x: int, y: int) -> int:
    return (x + y) % pow(2, 32)


def left_circular_shift(x: int, shift: int) -> int:
    return (pow(2, 32) - 1) & (x << shift | x >> (32 - shift))


def arx_mixer(data: list) -> list[int]:
    data[0] = modulo_addition(data[0], data[3])
    data[1] ^= data[0]
    data[1] = left_circular_shift(data[1], 13)
    data[2] = modulo_addition(data[1], data[2])
    data[3] ^= data[2]
    data[3] = left_circular_shift(data[3], 17)
    data[0] = modulo_addition(data[3], data[0])
    data[1] ^= data[0]
    data[1] = left_circular_shift(data[1], 9)
    data[2] = modulo_addition(data[1], data[2])
    data[3] ^= data[2]
    data[3] = left_circular_shift(data[3], 7)

    return [data[1], data[2], data[3], data[0]]


def key_schedule_mixer(outer_state: list, constants: tuple) -> list:
    def arx_column(state: list) -> list:
        return [
            arx_mixer([state[0][0], state[1][0], state[2][0], state[3][0]]),
            arx_mixer([state[0][1], state[1][1], state[2][1], state[3][1]]),
            arx_mixer([state[0][2], state[1][2], state[2][2], state[3][2]]),
            arx_mixer([state[0][3], state[1][3], state[2][3], state[3][3]]),
        ]

    def arx_diagonal(state: list) -> list:
        return [
            arx_mixer([state[0][0], state[1][1], state[2][2], state[3][3]]),
            arx_mixer([state[0][1], state[1][2], state[2][3], state[3][0]]),
            arx_mixer([state[0][2], state[1][3], state[2][0], state[3][1]]),
            arx_mixer([state[0][3], state[1][0], state[2][1], state[3][2]]),
        ]

    # add constants to outer state
    inner_state = [
        xor_array(data_01=outer_state[i], data_02=constants[i], length=4) for i in range(4)
    ]

    # apply arx column
    res_column = arx_column(state=inner_state)

    # return result of arx diagonal
    return arx_diagonal(state=res_column)


def key_schedule(secret_key: list[int]) -> list[int]:
    def large_arx_mixer(state: list, constants: tuple, repetitions: int) -> list:
        for _ in range(repetitions):
            res = key_schedule_mixer(outer_state=state, constants=constants)
            state = res

        return state

    # SHA3-512 hash for "Fragment-256 is My Passion Project."
    CONSTANTS = (
        (0x2AB65BFE, 0x653F80E5, 0x29C155CD, 0x875BEDAA),
        (0x9F71C971, 0x95781153, 0xDD2A78E5, 0x43BDE4EA),
        (0x54482CC5, 0xBEAE3B9D, 0xD8036E07, 0xF66C8B96),
        (0x40B60E6D, 0xB5CEF043, 0x44707BD1, 0xB419E27D),
    )

    # Base key state
    key_state = [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]

    # prepare key further; split bytes to 128bits
    k0, k1 = prepare_data(data=secret_key, length=16, to_integer=False)

    # prepare key further; split bytes to 32bits & to integers
    key_01 = prepare_data(data=k0, length=4, to_integer=True)
    key_02 = prepare_data(data=k1, length=4, to_integer=True)

    # update buffer 00 with key_01
    key_state[0] = xor_array(data_01=key_state[0], data_02=key_01, length=4)

    # apply arx box with 4 repetitions
    key_state = large_arx_mixer(state=key_state, constants=CONSTANTS, repetitions=4)

    # update buffer 00 with key_02
    key_state[0] = xor_array(data_01=key_state[0], data_02=key_02, length=4)

    # apply extended arx box with 12 (8 mixer + 4 base) repetitions to mix key state further
    key_state = large_arx_mixer(state=key_state, constants=CONSTANTS, repetitions=12)

    # number of rounds = NUNBER_OF_KEYS / 2
    NUNBER_OF_KEYS = 64
    round_keys = []

    for _ in range(NUNBER_OF_KEYS):
        round_keys.append(key_state[0])
        key_state = large_arx_mixer(state=key_state, constants=CONSTANTS, repetitions=4)

    return [round_keys[x : x + 2] for x in range(0, len(round_keys), 2)]


def permutation_function(data: list) -> list:
    for _ in range(4):
        data[0] = modulo_addition(x=data[0], y=data[1])
        data[2] = modulo_addition(x=data[2], y=data[3])
        data[1] = modulo_addition(x=data[0], y=(2 * data[1]))
        data[3] = modulo_addition(x=data[2], y=(2 * data[3]))

        data = [data[1], data[2], data[3], data[0]]

    return [[data[0], data[1]], [data[2], data[3]]]


def round_function(x: list, y: list, round_keys: list) -> list:
    # add first key set
    res_01 = xor_array(data_01=x + y, data_02=round_keys[0], length=4)
    res_02 = arx_mixer(data=res_01)

    # add second key set
    res_03 = xor_array(data_01=res_02, data_02=round_keys[1], length=4)
    res_04 = arx_mixer(data=res_03)

    # return result of permutation function
    return permutation_function(data=res_04)


def encrypt(data: list, round_keys: list) -> list:
    data = prepare_data(data=data, length=4, to_integer=True)
    a, b, c, d = [data[x : x + 2] for x in range(0, len(data), 2)]

    for rk in round_keys:
        e, f = round_function(x=a, y=b, round_keys=rk)
        g = xor_array(data_01=e, data_02=c, length=2)
        h = xor_array(data_01=f, data_02=d, length=2)

        c = a
        d = b
        a = g
        b = h

    return [c, d, a, b]


def decrypt(data: list, round_keys: list) -> list:
    # reverse round keys
    reversed_round_keys = round_keys.copy()
    reversed_round_keys.reverse()

    result = encrypt(data=data, round_keys=reversed_round_keys)

    return result
