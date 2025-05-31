a = 1.234567888889
b = 1.234567888888
epsilon = 1e-15

diff = abs(a - b)
if diff < epsilon:
    print(f"{a} ≈ {b} (within epsilon)")
elif a - b >= epsilon:
    print(f"{a} > {b}")
elif b - a >= epsilon:
    print(f"{a} < {b}")
    