import math
import numpy as np

def magnitude(vector):
    return math.sqrt(sum(pow(element, 2) for element in vector))

def normalize(vector):
    norm = np.linalg.norm(vector)
    if norm == 0: 
       return vector
    return vector / norm

for i in range(3):
    print(i)