"""
# ~2.9 seconds for 0.9 Gigabits using PYTHON 3.12

Will implement in 'C' after i get a job!
"""


from core import bytes_to_integers, generate_random_bytes
from enc import encipher
from ksa import key_schedule


def main() -> None:
    secret_key = generate_random_bytes(size=32)
    kbti = bytes_to_integers(secret_key)

    round_keys = key_schedule(key=kbti)

    iv = generate_random_bytes(size=32)
    ibti = bytes_to_integers(bytestring=iv)

    round_key_sets = [round_keys[:6], round_keys[6:12], round_keys[12:18], round_keys[18:24]]

    cipher_data = encipher(d0=ibti[:4], d1=ibti[4:], round_keys=round_key_sets)


if __name__ == "__main__":
    main()
