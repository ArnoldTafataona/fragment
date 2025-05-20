import math

BLOCKSIZE = 256
COUNTER_LIMIT = pow(2, 32)

# 1073741824 bytes <1GB>
number = 1073741824 / BLOCKSIZE
print(number)

if number < COUNTER_LIMIT:
    rounded_number = math.ceil(number)

    print(f"counter = {rounded_number}")
    print(f"size = {rounded_number * BLOCKSIZE} bytes.")
else:
    print("[ERROR] data length exceeds counter limit.")
