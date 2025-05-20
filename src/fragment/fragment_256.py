"""Fragment-256 Core Functionality."""

import secrets
import time


def b2i(string: bytes, length: int) -> list[int]:
    """Split bytestring into a list of integers"""
    return [int.from_bytes(string[x : x + length], "big") for x in range(0, len(string), length)]


def i2b(integers: list) -> bytes:
    """List of integers to bytestring"""
    return b"".join([x.to_bytes(4, "big") for x in integers])


def modulo_addition(x: int, y: int) -> int:
    """Modulo Additon"""
    return (x + y) % pow(2, 32)


def bit_shift(x: int, shift: int) -> int:
    """Left circular bit shift"""
    return (pow(2, 32) - 1) & (x << shift | x >> (32 - shift))


def arx_mixer(data: list) -> list[int]:
    """Four branch ARX network.

    Args:
        data (list): Encrypted data.

    Returns:
        list[int]: Diffused data.
    """

    data[0] = modulo_addition(data[0], data[3])
    data[1] ^= data[0]
    data[1] = bit_shift(data[1], 13)
    data[2] = modulo_addition(data[1], data[2])
    data[3] ^= data[2]
    data[3] = bit_shift(data[3], 17)
    data[0] = modulo_addition(data[3], data[0])
    data[1] ^= data[0]
    data[1] = bit_shift(data[1], 5)
    data[2] = modulo_addition(data[1], data[2])
    data[3] ^= data[2]
    data[3] = bit_shift(data[3], 7)

    # Word permutation of updated data
    perm_data = [data[1], data[2], data[3], data[0]]

    return perm_data


def pht_mixer(data: list) -> list:
    """4 round feistel network that uses Pseudo-Hadamard transform for diffusion."""

    def pht(x: int, y: int) -> tuple:
        """Pseudo-Hadamard transform"""

        x = modulo_addition(x=x, y=y)
        y = modulo_addition(x=x, y=(2 * y))

        return x, y

    a, b, c, d = data

    for _ in range(4):
        e, f = pht(x=a, y=b)
        g = e ^ c
        h = f ^ d

        # Update values
        c = a
        d = b
        a = g
        b = h

    return [c, d, a, b]


def key_schedule_mixer(key_state: list, constants: tuple, repetitions: int):
    def mixer(key_state: list, constants: tuple) -> list:
        # Add constants
        updated_state = [key_state[x] ^ constants[x] for x in range(4)]

        # Apply ARX mixer
        result = arx_mixer(data=updated_state)

        return result

    for _ in range(repetitions):
        result = mixer(key_state=key_state, constants=constants)
        key_state = result

    return key_state


def key_schedule(encryption_key: bytes) -> list:
    # MD5 Hash for: FRAGMENT-256 Is My Passion Project. Do Not Use. Not Tested. Just Look.
    CONSTANTS = (0xB248E256, 0x6E86B410, 0x10A50869, 0x6947535F)

    # Initial key state.
    key_state = [0, 0, 0, 0]

    # Convert bytesring to list of integers
    key_b2i = b2i(string=encryption_key, length=4)

    # ==== Key absorbtion state
    for key in key_b2i:
        key_state[0] ^= key

        # Apply 4 round ARX mixer
        key_state = key_schedule_mixer(key_state=key_state, constants=CONSTANTS, repetitions=4)

    # ==== Extended key mixing state
    # Apply 8 round ARX mixer
    key_state = key_schedule_mixer(key_state=key_state, constants=CONSTANTS, repetitions=8)

    # ==== Key squeezing state
    NUMBER_OF_KEYS = 256
    round_keys = []

    for round_number in range(NUMBER_OF_KEYS):
        # XOR key_state[0] with round number
        key_state[0] ^ round_number

        # squeeze out 32bit key
        round_keys.append(key_state[0])

        # Apply 4 round ARX mixer
        key_state = key_schedule_mixer(key_state=key_state, constants=CONSTANTS, repetitions=4)

    # ==== Sort round keys
    # Temporary rounds key list. Split keys into sets[lists] containing for 4-32bit keys.
    t_round_keys = [round_keys[i : i + 4] for i in range(0, NUMBER_OF_KEYS, 4)]

    # Final round key list. Split keys sets to match number keys of keys required in a round.
    # 8-32bit keys per round, over 2 iterations. 4 keys, something, 4 keys, and something.
    f_round_keys = [t_round_keys[i : i + 2] for i in range(0, len(t_round_keys), 2)]

    return f_round_keys


def round_function(m: int, n: int, o: int, p: int, round_keys: list) -> list:
    data = [m, n, o, p]

    # Add first key set
    data = [data[x] ^ round_keys[0][x] for x in range(4)]

    # Apply ARX mixer
    data = arx_mixer(data=data)

    # Add second key set
    data = [data[x] ^ round_keys[1][x] for x in range(4)]

    # Apply ARX mixer
    data = arx_mixer(data=data)

    # Apply permutation function
    data = pht_mixer(data=data)

    return data


def encrypt(data: list, round_keys: list) -> list:
    if not isinstance(data, list):
        data = b2i(string=data, length=4)

    a, b, c, d, e, f, g, h = data

    for round_key_set in round_keys:
        w, x, y, z = round_function(m=a, n=b, o=c, p=d, round_keys=round_key_set)
        m = e ^ w
        n = f ^ x
        o = g ^ y
        p = h ^ z

        # Update values
        e = a
        f = b
        g = c
        h = d
        a = m
        b = n
        c = o
        d = p

    return [e, f, g, h, a, b, c, d]


def decrypt(data: list, round_keys: list) -> list:
    if not isinstance(round_keys, list):
        round_keys = key_schedule(round_keys)

    if not isinstance(data, list):
        data = b2i(string=data, length=4)

    # reverse round keys
    reversed_round_keys = round_keys.copy()
    reversed_round_keys.reverse()

    result = encrypt(data=data, round_keys=reversed_round_keys)

    return result


def main() -> None:
    secret_key = secrets.token_bytes(32)
    iv = secrets.token_bytes(32)

    a = time.perf_counter()

    ROUND_KEYS = key_schedule(encryption_key=secret_key)

    b = time.perf_counter()

    enc_data = encrypt(data=iv, round_keys=ROUND_KEYS)

    dec_data = decrypt(data=enc_data, round_keys=ROUND_KEYS)

    print(f"original text: {i2b(b2i(string=iv, length=4)).hex()}")
    print(f"- cipher text: {i2b(enc_data).hex()}")
    # print(f"-- plain text: {i2b(dec_data).hex()}")

    print(f"Completed {len(ROUND_KEYS)} rounds in {b-a} second(s).")


if __name__ == "__main__":
    main()
