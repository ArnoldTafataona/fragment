import secrets
import time
from itertools import chain

from fragment_256 import decrypt, encrypt, key_schedule, prepare_data


def i2b(data: list[int]) -> bytes:
    unnested_data = list(chain(*data))
    return b"".join([x.to_bytes(4, "big") for x in unnested_data])


def main() -> None:
    secret_key = secrets.token_bytes(32)
    iv = secrets.token_bytes(32)

    ROUND_KEYS = key_schedule(secret_key=secret_key)

    a = time.perf_counter()

    cipher_txt = encrypt(data=iv, round_keys=ROUND_KEYS)

    b = time.perf_counter()

    plain_text = decrypt(data=i2b(cipher_txt), round_keys=ROUND_KEYS)

    t = prepare_data(data=iv, length=4, to_integer=True)
    u = [t[x : x + 2] for x in range(0, len(t), 2)]

    print(f"Original text: {i2b(u).hex()}")
    print(f"- Cipher text: {i2b(cipher_txt).hex()}")
    print(f"-- Plain text: {i2b(plain_text).hex()}")

    print(f"Took {b-a} second(s) to complete {len(ROUND_KEYS)} rounds.")


if __name__ == "__main__":
    main()
