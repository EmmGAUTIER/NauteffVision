#!/usr/bin/python3

import calculs
import test_calculs
import math
from cmpfloats import cmpFloats
from datetime import datetime

from test_data import test_data

if __name__ == "__main__":
    ############################################################
    # Test du type dataAttitude
    ###########################################################
    now = datetime.now()
    formatted_date = now.strftime("%Y-%m-%d %H:%M:%S")
    print("******************************************************************************")
    print("*  NauteffVision Tests unitaires                                             *")
    print("******************************************************************************")
    print ()
    print(f"{formatted_date}")
    print()

    print(f"Essais : calculs.py")
    test_calculs.test_calculs()
    print("")

    print(f"Essais : data.py")
    test_data()
    print("")

    print("Fin")
