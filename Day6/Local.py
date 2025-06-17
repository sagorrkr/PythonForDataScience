import time

#local = time.localtime(time.time())
local = time.asctime(time.localtime(time.time()))
print("Current TIme: ", local)