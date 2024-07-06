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

# import time

class DataListener:

    def get_data_list_in(self):
        return []

    def put_data(self, data):
        return


class DataEmitter:
    def __init__(self):
        self.queue = None

    def get_data_list_out(self):
        return []

    def setDataQueue(self, queue):
        self.queue = queue
        return


class dataType:

    def __init__(self, n, t):
        self.type = t
        self.name = n


class Data:
    def __init__(self, dtype="?", timestamp=None, originalFrame=None,
                 provenance=None, values=None):
        self.type = dtype
        self.valid = None
        self.timestamp = timestamp
        self.originalFrame = originalFrame
        self.provenance = provenance
        self.values = values


def __str__(self):
    return "Data"


class dataNMEA0183(Data):
    def __init__(self, timeStamp, provenance, originalFrame):
        super().__init__(timeStamp, provenance, originalFrame)
        self.type = "NMEA"


class dataDPT(dataNMEA0183):
    def __init__(self, timeStamp, provenance, originalFrame):
        super().__init__(timeStamp, provenance, originalFrame)
        self.type = "DPT"
        self.depth = 0.
        self.offset = 0.


class dataSysTime(Data):
    def __init__(self, timeStamp):
        super().__init__(timeStamp, "SYS", "")

        self.type = "TIME"


class dataNauteff(Data):
    def __init__(self, timeStamp, provenance, originalFrame):
        super().__init__(timeStamp, provenance, originalFrame)


class dataHeading(Data):
    def __init__(self, timeStamp, provenance, originalFrame):
        super().__init__(timeStamp, provenance, originalFrame)
        originalFrame.split()
        self.heading = int(originalFrame)


def dataDecode(timeStamp, orig, frame: str) -> Data:
    # print("Trame à analyser", int(timeStamp), orig, frame)
    # ts = time.time()

    d = dataDecodeNMEA0183(timeStamp, orig, frame)
    if d is not None: return d

    s = frame.split()
    if len(s) >= 2 :
        if s[0] == "HDG/M":
            print("Data : cap")
            val = int(s[1])
            datah = Data("HDG/M", timeStamp, frame, "Nauteff/AP",
                              {"Heading/Mag":val})
            return datah


    # return data

    # type = None
    pass

    d = Data()
    d.timestamp = timeStamp
    d.provenance = orig
    d.originalFrame = frame
    d.type = "?"
    d.values = None
    return d


def dataDecodeNMEA0183(timeStamp, orig, frame) -> dataNMEA0183:
    d = None
    l = len(frame)
    # print("Taille : ", l, type(l))
    if l < 10 or l > 82:
        return None
    if frame[0] != "$":
        return None
    if frame[l - 1] == '\n' or frame[l - 1] == '\r':
        l = l - 1
    if frame[l - 1] == '\n' or frame[l - 1] == '\r':
        l = l - 1
    # checksum = frame[l - 3: l]
    # print("checksum : ", checksum)
    frame = frame[0: l - 3]
    ellist = frame.split(',')
    ftype = ellist[0][3:]

    if type == "MWV":  # Wind speed and angle
        pass
    elif ftype == "DBK":  # Depth below kell
        pass
    elif ftype == "DBS":  # Depth below surface, obsolete
        pass
    elif ftype == "DBT":  # Depth below Transducer, obsolete
        pass
    elif ftype == "DPT":  # Depth of water
        #d.type = "DPT"
        d = dataDPT(timeStamp, orig, frame)
        d.depth = float(ellist[1])
        d.offset = float(ellist[2])
        if d.offset >= 0.:
            d.depthBelowSurface = d.depth + d.offset
            d.depthBelowKeel = None
        else:
            d.depthBelowSurface = None
            d.depthBelowKeel = d.depth + d.offset

    elif ftype == "MTW":  # Mean Temperature of water
        pass
    elif ftype == "MWV":  # Wind speed and angle
        pass
    else:
        return None

    print("Trame décomposée : ", ellist, orig)
    print("Type", ellist[0][3:])

    return d
