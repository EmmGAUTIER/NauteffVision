#!/usr/bin/python3

import math
import time

from cmpfloats import cmpFloats
from data import dataDecode


def test_data():

    ############################################################
    # Test du type dataAttitude
    ############################################################
    frame = "$GPGGA,123519,4851.502,N,00217.668,E,1,08,0.9,314.1,M,46.9,M, , *42"
    frame = "$GPGGA,073410,4835.1160,N,00350.1682,W,1,5,1.60,11,M,,,,*29"
    timestamp = time.time()
    data_test = dataDecode(timestamp, "SP1", frame)
    # print (data_test)





