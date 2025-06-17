import pickle

with open("/Users/sagor/Desktop/PythonForDataScience/101/Day5/LX20240507002.pkl", 'rb') as f:
    reconstructed_data = pickle.load(f)

print("Reconstructed dictionary:")
print(reconstructed_data)