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

import json
import sys
from distributeur import Distributeur
import argparse

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='df_report: statistiques exploratoires pour aborder un jeu de données.')
    parser.add_argument('--config',        default = 'NauteffVision.json')
    args = vars(parser.parse_args())
    cfgfilename  = args["config"]

    print("Nauteff Vision Let's go!")
    file = open(cfgfilename, "r")
    NVConfig = json.load(file)
    file.close()

    distributeur = Distributeur(NVConfig)

    print("Nauteff Vision , good bye!")
    sys.exit(0)
