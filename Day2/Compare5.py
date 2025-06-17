a = 1.234567888889
b = 1.234567888888
epsilon = 1e-15
diff = abs(a - b)


if a > b + epsilon:
    print("a > b ")
if a < b - epsilon:
    print("a < b ")
if (diff < epsilon) or (a > b + epsilon):
    print("a >= b ")
if (diff < epsilon) or (a < b - epsilon):
    print("a <= b ")
if diff < epsilon:
    print("a == b ")
else:
    print("a != b")