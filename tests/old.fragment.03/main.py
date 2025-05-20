from fragment_256 import (
    bytes_to_integers,
    decrypt,
    encrypt,
    generate_random_bytes,
    integer_to_bytes,
    key_schedule,
)


def main() -> None:
    message = ">>> The cake is [REDACTED]. <<<"
    key = generate_random_bytes(size=32)
    iv = generate_random_bytes(size=32)

    round_keys = key_schedule(secret_key=key)

    plain_text = bytes_to_integers(iv)

    print("ENCRYPTION".center(80, "-"))

    cipher_text = encrypt(data=plain_text, round_keys=round_keys)

    print(f"plaintext  = {integer_to_bytes(plain_text)}", len(integer_to_bytes(plain_text)))
    print(f"ciphertext = {integer_to_bytes(cipher_text)}", len(integer_to_bytes(cipher_text)))

    print("DECRYPTION".center(80, "-"))

    print(f"ciphertext = {integer_to_bytes(cipher_text)}", len(integer_to_bytes(cipher_text)))

    plain_text = decrypt(data=cipher_text, round_keys=round_keys)

    print(f"plaintext  = {integer_to_bytes(plain_text)}", len(integer_to_bytes(plain_text)))

    if iv.hex() == integer_to_bytes(plain_text):
        print("encryption & decryption cycle successful!".center(80, "-").upper())
    else:
        print("encryption & decryption cycle failed!".center(80, "-").upper())


if __name__ == "__main__":
    main()
