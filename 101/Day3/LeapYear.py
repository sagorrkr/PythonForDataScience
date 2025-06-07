year = int(input("Enter a year: "))
if year % 4 == 0:
    if  (year % 100 != 0 or year % 400 == 0): 
        print("Leap year.")
    else:
        print("Not Leap Year.")
else:
    print("Not a leap year.")