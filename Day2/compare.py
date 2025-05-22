a = 1.234567888888
b = 1.234567888889
epsilon = 1e-15  
if abs(a - b) < epsilon:
    print(" equal")
elif a > b + epsilon:  
    print("a is greater than or equal to b")
elif a < b - epsilon: 
    print("a is less than or equal to b")
