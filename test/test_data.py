#!/usr/bin/python3

import calculs
import math
from cmpfloats import cmpFloats

def test_answer():

    ############################################################
    # Test du type dataAttitude
    ############################################################
    assert cmpFloats(calculs.rad2deg(-3.5*math.pi) ,   0.0) == True





