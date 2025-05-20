import hashlib

const = "FRAGMENT-256 Is My Passion Project. Do Not Use. Not Tested. Just Look.".encode()
hash = hashlib.md5(const).hexdigest()
print(f"HASH = '{hash}'")

t0 = [f"0x{hash[x : x + 8]}".upper() for x in range(0, len(hash), 8)]
t1 = [tuple(t0[x : x + 4]) for x in range(0, len(t0), 4)]

print("CONSTANTS =", str(tuple(t1)).replace("'", ""))

CONSTANTS = ((0xB248E256, 0x6E86B410, 0x10A50869, 0x6947535F),)

for index, keys in enumerate(CONSTANTS, start=1):
    print(f"CONSTANT {index} : {[x.bit_length() for x in keys]} {keys}")
