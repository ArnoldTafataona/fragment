from random import randint


def logical_not(x):
    return ~x


def logical_and(x, y):
    return x & y


def logical_xor(x, y):
    return x ^ y


def evaluate_expression_a(x, y, z):
    not_y = logical_not(y)
    and_result = logical_and(not_y, z)
    xor_result = logical_xor(and_result, x)
    return xor_result


def evaluate_expression_b(x, y, z):
    return (~y & z) ^ x


# Example usage:
x = randint(0, pow(2, 32))
y = randint(0, pow(2, 32))
z = randint(0, pow(2, 32))

res_a = evaluate_expression_a(x, y, z)
res_b = evaluate_expression_b(x, y, z)

print(f"x={x}, y={y}, z={z}")
print("Result A:", res_a)
print("Result B:", res_b)
