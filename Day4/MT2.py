# The outer loop iterates through each number from 1 to 10.
# Each 'i' represents the base number for the current row.
for i in range(1, 8):
    

    padding = " " * (9 - i) * 14
    print(padding, end="")

    for j in range(1, i + 1):
        result = i * j
        print(f"{i} * {j} = {result}", end="   ")
        
    print()

