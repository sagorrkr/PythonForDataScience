input1 = input("Please input a sentense: ")

words = input1.split()

reversedWord = words[:: -1]
rev = " ".join(reversedWord) 

print(rev)