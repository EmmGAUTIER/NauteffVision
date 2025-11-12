#!/usr/bin/python3

import calculs
import math
from cmpfloats import cmpFloats # Comparing floats

def test_calculs():

    # radians of angles start from left and grow counterclockwise
    # degrees of angles start fom top and grow clockwise.

    ############################################################
    # Test de la fonction rad2deg converting radians to degrees.
    ############################################################
    assert cmpFloats(calculs.rad2deg(0)            ,  90.0) == True
    assert cmpFloats(calculs.rad2deg(math.pi/2.)   ,   0.0) == True
    assert cmpFloats(calculs.rad2deg(math.pi/4.)   ,  45.0) == True
    assert cmpFloats(calculs.rad2deg(math.pi)      , 270.0) == True
    assert cmpFloats(calculs.rad2deg(-math.pi)     , 270.0) == True
    assert cmpFloats(calculs.rad2deg(2.*math.pi)   ,  90.0) == True
    assert cmpFloats(calculs.rad2deg(3.*math.pi)   , 270.0) == True
    assert cmpFloats(calculs.rad2deg(3.5*math.pi)  , 180.0) == True
    assert cmpFloats(calculs.rad2deg(-3.5*math.pi) ,   0.0) == True

    ############################################################
    # Test de la fonction deg2rad converting degrees to radians
    ############################################################
    assert cmpFloats(calculs.deg2rad(0.0),     math.pi/2.0)    == True
    assert cmpFloats(calculs.deg2rad(45.0),    math.pi/4.0)    == True
    assert cmpFloats(calculs.deg2rad(90.0),    0.0)            == True
    assert cmpFloats(calculs.deg2rad(180.0),   1.5 * math.pi)  == True
    assert cmpFloats(calculs.deg2rad(270.0),   math.pi)        == True
    assert cmpFloats(calculs.deg2rad(360),     math.pi/2.0)    == True
    assert cmpFloats(calculs.deg2rad(405),     math.pi/4.0)    == True
    assert cmpFloats(calculs.deg2rad(720.0),   math.pi/2.0)    == True
    assert cmpFloats(calculs.deg2rad(-90.),    math.pi)        == True
    assert cmpFloats(calculs.deg2rad(-270.0),  0.0)            == True
    assert cmpFloats(calculs.deg2rad(-360.0),  math.pi/2.0)    == True
    assert cmpFloats(calculs.deg2rad(-405),    0.75 * math.pi) == True




