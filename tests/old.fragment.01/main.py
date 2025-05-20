import time

import fragment


def main() -> None:
    secret_key = fragment.generate_random_bytes(size=fragment.BYTE_LENGTH)
    init_vector = fragment.generate_random_bytes(size=fragment.BYTE_LENGTH)

    iv_words = fragment.split_into_words(container=fragment.split_bytestring(bytestring=init_vector))

    key_words = fragment.split_into_words(container=fragment.split_bytestring(bytestring=secret_key))

    round_keys = fragment.ksa(secret_key=key_words)

    print(iv_words)
    res_enc = fragment.fragment_enc(iv_words, round_keys)
    print(res_enc)


if __name__ == "__main__":
    main()
