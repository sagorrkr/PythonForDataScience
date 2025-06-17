import pickle

data1 = {
    'Name': "罗酷",
    'ID': "LX20240513004",
    'Major': "Information and Communication Engineering",
    "School" : "Hohai University",
    "Course" : "Numerical Computing."
}

with open("/Users/sagor/Desktop/PythonForDataScience/101/Day5/lx20240513004.pkl", 'wb') as f:
    pickle.dump(data1, f)

print("Dictionary stored in data.pkl")