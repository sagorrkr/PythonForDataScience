a = 1.23456789
b = 1.234567889
epsilon = 1e-12  

if abs(a - b) < epsilon:
    print("Equal")
elif a >= b + epsilon: 
    print("a greater than b")
elif a <= b - epsilon:  
    print("a less than b")
