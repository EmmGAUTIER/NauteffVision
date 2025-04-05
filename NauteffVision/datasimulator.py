#!/usr/bin/python3
###############################################################################
#
# This file is part of the Nauteff Autopilot project.
#
# Copyright (C) 2023 Nauteff https://nauteff.com
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import time
# import threading
# import os
import sys
import argparse

# import data
# import math

NVConfigDemo = {
    "title": "Nauteff Vision / Let's start ",

    "demo": "",

    "computations": {
        "att": {
            "type": "attitude",
            "id": "att",
            "source": "E1",
            "destination": "S3"
        }
    },
    "dashboard" : {
        "title" : "Nauteff Vision for Kreiz Avel",
        "instruments": {
            "COMPASS_1":{
                "type": "compass",
                "cell_origx": 1,
                "cell_origy": 0,
                "cell_width": 2,
                "cell_height": 2,
                "origin": "AP1"
            },
            "WND_1":{
                "type": "wind",
                "cell_origx": 3,
                "cell_origy": 0,
                "cell_width": 2,
                "cell_height": 2
            },
            "SPEED":{
                "type": "speed",
                "cell_origx": 5,
                "cell_origy": 0,
                "cell_width": 2,
                "cell_height": 2,
                "unit" : "kts",
                "min_val" : 0,
                "max_val" : 16
            },

            "ATT_1" :
                {
                    "type": "attitude",
                    "cell_origx": 1,
                    "cell_origy": 2,
                    "cell_width": 3,
                    "cell_height": 2,
                    "title": "Assiette",
                    "origin": "AP1"
                },
            "CLOCK_LOCAL" : {
                "type":       "clock",
                "cell_origx": 6,
                "cell_origy": 2,
                "cell_width": 1,
                "cell_height": 1,
                "title" :     "Brest",
                "time_zone" : "Europe/Paris"
            },

            "CLOCK_RUN" : {
                "type":       "clock",
                "cell_origx": 5,
                "cell_origy": 2,
                "cell_width": 1,
                "cell_height": 1,
                "title" :     "Saint Denis de la Réunion",
                "time_zone" : "Indian/Reunion"
            },
            "AP_MOT":
                {
                    "type": "APmotor",
                    "cell_origx": 4,
                    "cell_origy": 2,
                    "cell_width": 1,
                    "cell_height": 1
                }, "AP_CTL" :
                {
                    "type": "APcontrol",
                    "cell_origx": 4,
                    "cell_origy": 3,
                    "cell_width": 3,
                    "cell_height": 1
                }
        }
    }

}


sw = [
    "$GPGLL,4835.1174,N,00350.1614,W,073214,A*36\r\n",
    "$GPRMB,A,3.21,L,,,4851.5887,N,00320.9741,W,25.34,49.3,0.0,A*0D\r\n",
    "$GPRMC,073214,A,4835.1174,N,00350.1614,W,0.0,0.0,300317,4.0,W*7A\r\n",
    "$SDDBT,5.4,f,1.6,M,0.9,F*09\r\n",
    "$SDDPT,1.6,-0.5,*54\r\n",
    "$GPGLL,4835.1176,N,00350.1613,W,073216,A*31\r\n",
    "$GPRMB,A,3.21,L,,,4851.5887,N,00320.9741,W,25.34,49.3,0.0,A*0D\r\n",
    "$GPRMC,073216,A,4835.1176,N,00350.1613,W,0.0,0.0,300317,4.0,W*7D\r\n",
    "$SDDBT,5.5,f,1.7,M,0.9,F*09\r\n",
    "$SDDPT,1.7,-0.5,*55\r\n",
    "$GPGLL,4835.1180,N,00350.1610,W,073218,A*35\r\n",
    "$GPRMB,A,3.21,L,,,4851.5887,N,00320.9741,W,25.34,49.3,0.2,A*0F\r\n",
    "$GPRMC,073218,A,4835.1180,N,00350.1610,W,0.3,0.0,300317,4.0,W*7A\r\n",
    "$SDDBT,5.4,f,1.6,M,0.9,F*09\r\n",
    "$SDDPT,1.6,-0.5,*54\r\n",
    "$GPGLL,4835.1186,N,00350.1606,W,073220,A*3F\r\n",
    "$GPRMB,A,3.21,L,,,4851.5887,N,00320.9741,W,25.34,49.3,0.2,A*0F\r\n",
    "$GPRMC,073220,A,4835.1186,N,00350.1606,W,0.3,0.0,300317,4.0,W*70\r\n",
    "$SDDBT,5.3,f,1.6,M,0.9,F*0E\r\n",
    "$SDDPT,1.6,-0.5,*54\r\n",
    "$GPGLL,4835.1191,N,00350.1601,W,073222,A*3C\r\n",
    "$GPRMB,A,3.21,L,,,4851.5887,N,00320.9741,W,25.34,49.3,0.0,A*0D\r\n",
    "$GPRMC,073222,A,4835.1191,N,00350.1601,W,0.0,0.0,300317,4.0,W*70\r\n",
    "$SDDBT,5.3,f,1.6,M,0.9,F*0E\r\n",
    "$SDDPT,1.6,-0.5,*54\r\n",
    "$GPGLL,4835.1195,N,00350.1599,W,073224,A*3C\r\n",
    "$GPRMB,A,3.21,L,,,4851.5887,N,00320.9741,W,25.34,49.3,0.2,A*0F\r\n",
    "$GPRMC,073224,A,4835.1195,N,00350.1599,W,0.3,0.0,300317,4.0,W*73\r\n",
    "$SDDBT,5.3,f,1.6,M,0.9,F*0E\r\n",
    "$SDDPT,1.6,-0.5,*54\r\n",
    "$GPGLL,4835.1197,N,00350.1598,W,073226,A*3D\r\n",
    "$GPRMB,A,3.21,L,,,4851.5887,N,00320.9741,W,25.34,49.3,0.0,A*0D\r\n",
    "$GPRMC,073226,A,4835.1197,N,00350.1598,W,0.0,0.0,300317,4.0,W*71\r\n",
    "$SDDBT,5.3,f,1.6,M,0.9,F*0E\r\n",
    "$SDDPT,1.6,-0.5,*54\r\n",
    "$GPGLL,4835.1199,N,00350.1600,W,073228,A*3F\r\n",
    "$GPRMB,A,3.21,L,,,4851.5887,N,00320.9741,W,25.34,49.3,0.0,A*0D\r\n",
    "$GPRMC,073228,A,4835.1199,N,00350.1600,W,0.0,0.0,300317,4.0,W*73\r\n",
    "$SDDBT,5.3,f,1.6,M,0.9,F*0E\r\n",
    "$SDDPT,1.6,-0.5,*54\r\n",
    "$GPGLL,4835.1199,N,00350.1602,W,073230,A*34\r\n",
    "$GPRMB,A,3.21,L,,,4851.5887,N,00320.9741,W,25.34,49.3,0.0,A*0D\r\n",
    "$GPRMC,073230,A,4835.1199,N,00350.1602,W,0.0,0.0,300317,4.0,W*78\r\n",
    "$SDDBT,5.5,f,1.7,M,0.9,F*09\r\n",
    "$SDDPT,1.7,-0.5,*55\r\n",
    "$GPGLL,4835.1201,N,00350.1603,W,073232,A*35\r\n",
    "$GPRMB,A,3.21,L,,,4851.5887,N,00320.9741,W,25.34,49.3,0.0,A*0D\r\n",
    "$GPRMC,073232,A,4835.1201,N,00350.1603,W,0.0,0.0,300317,4.0,W*79\r\n",
    "$SDDBT,5.6,f,1.7,M,0.9,F*0A\r\n",
    "$SDDPT,1.7,-0.5,*55\r\n"]

sw = [

    "ATTITUDE 0.0     0.00 -0.0",
    "WIND 25  10.5",
    "ATTITUDE 0.05    0.10 -0.10",
    "WIND 30  10.5",
    "ATTITUDE 0.10    0.20 -0.30",
    "WIND 40  10.5",
    "ATTITUDE 0.15    0.30 -0.40",
    "WIND 50  10.5",
    "ATTITUDE 0.23    0.40 -0.45",
    "WIND 65  14.5",
    "ATTITUDE 0.43    0.50 -0.38",
    "WIND 66  13.5",
    "ATTITUDE 0.48    0.50 -0.32",
    "ATTITUDE 0.53    0.50 -0.28",
    "WIND -35  10.5",
    "ATTITUDE 0.58    0.50 -0.21",
    "ATTITUDE 0.65    0.50 -0.19",
    "WIND -38  11.5",
    "ATTITUDE 0.70    0.0 -0.17",
    "ATTITUDE 0.76    0.0 -0.12",
    "WIND -40  12.5",
    "ATTITUDE 0.83    0.00 -0.05"
]

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Simulateur de données pour NauteffVision')
    parser.add_argument('-o', help="Nom du fichier de sortie", default=None)
    args = vars(parser.parse_args())
    outFileName = args["o"]

    print("Sortie vers ", outFileName);

    if outFileName == None:
        outFile = sys.stdout
        pass
    else:
        outFile = open(outFileName, buffering=1, mode="w")
        pass

    # print ("Bonjour\r\n", file=outFile)

    i = 0
    while True:
        print(sw[i], file=outFile)
        i = i + 1 if i + 1 < len(sw) else 0
        time.sleep(0.5)
