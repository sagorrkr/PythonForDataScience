import pickle

data1 = {
    'a': [1, 2.0, 4+6j],
    'b': ("string", "unicode string"),
    'c': None
}

with open("/Users/sagor/Desktop/PythonForDataScience/101/Day5/data.pkl", 'wb') as f:
    pickle.dump(data1, f)

print("Dictionary stored in data.pkl")