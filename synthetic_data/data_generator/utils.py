import numpy as np

def sig(x):
 """
 It is the sigmoid activation function normally used in neural nets.
 A nice function for forcing a number between 0 and 1. 
 """
 return 1/(1 + np.exp(-x))