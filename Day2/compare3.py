a = 1.234567888889
b = 1.234567888888
epsilon = 1e-15

if abs(a - b) < epsilon:
    print("a == b")
if abs(a - b) >= epsilon:
    print("a != b")
if a > b + epsilon:
    print("a > b")
if a > b - epsilon:
    print("a >= b")
if a < b - epsilon:
    print("a < b")
if a < b + epsilon:
    print("a <= b")