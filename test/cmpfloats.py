
import math

def cmpFloats(a,b) :
    mag = math.fabs(a) + math.fabs(b)
    diff = math.fabs(a-b)
    if mag == 0 :
        eq = True
    elif diff / mag < 1.e-15 :
        eq = True
    else :
        eq = False
    return eq

