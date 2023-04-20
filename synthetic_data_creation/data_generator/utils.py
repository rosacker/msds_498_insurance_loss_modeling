from math import exp
import random

def sig(x):
    """
    It is the sigmoid activation function normally used in neural nets.
    A nice function for forcing a number between 0 and 1. 

    Using an approximation for speeeeed!
    """
    
    return 0.5 * (x / (1 + abs(x)) + 1)

def poisson(lam):
    # Shortcut poisson formula for speed!

    p_0 = (exp(-lam))
    p_gt_0 = 1 - p_0

    if p_gt_0 > random.uniform(0, 1):
        return 1
    else:
        return 0