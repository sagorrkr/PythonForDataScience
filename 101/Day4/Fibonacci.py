n = 100  
a, b = 0, 1
sequence = []

for _ in range(n):
    sequence.append(a)
    a, b = b, a + b

print(sequence)