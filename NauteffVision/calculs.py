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

import math

def deg2rad(angle):

    anglerad = math.pi/2.0 - (math.pi/180) * angle

    if anglerad >= 0.:
        anglerad = math.fmod(anglerad, 2.0 * math.pi)
    else:
        anglerad = 2.0 * math.pi + math.fmod(anglerad, 2.0 *math.pi)

    return anglerad

def rad2deg(angle):

    angledeg = 90. - (180/math.pi) * angle

    if angledeg >= 0. :
        angledeg = math.fmod(angledeg, 360.)
    else:
        angledeg = 360. + math.fmod(angledeg, 360.)

    return angledeg

