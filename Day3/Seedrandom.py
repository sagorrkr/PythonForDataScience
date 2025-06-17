import random
from datetime import datetime
int_seed = datetime.now().timestamp()
print(int_seed)
random.seed(int_seed)
number = random.randint(1, 10)
print(number) 
