d = {'Name': 'Angela Merkel', 'Country': 'Germany', 'Profession': 'Chancellor', 'Age': 60}

print("Type of d:", type(d))

print(d['Name'], d['Age'])

print("Keys:", d.keys())
print("Values:", d.values())
print("Items:", d.items())

print("\nIterating over items:")
for item in d.items():
    print(item)

print("\nIterating over values and their types:")
for value in d.values():
    print(f"Value: {value}, Type: {type(value)}")