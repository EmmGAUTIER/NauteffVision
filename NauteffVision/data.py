"""
This file is part of the Nauteff Autopilot project.

 Copyright (C) 2023 Nauteff https://nauteff.com

This library is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this library.  If not, see <http://www.gnu.org/licenses/>.
"""

"""
Autre documentation : à rédiger
"""

from abc import abstractmethod  # Abstract methods
import time

class DataListener:

    @abstractmethod
    def get_data_list_in(self) -> list:
        return []

    @abstractmethod
    def putData(self, data):
        return

class DataEmitter:
    def __init__(self, queue):
        self.queue = queue

    @abstractmethod
    def get_data_list_out(self) -> list:
        return []

    @abstractmethod
    def setDataQueue(self, queue):
        self.queue = queue
        return


class dataType:

    def __init__(self, n, t):
        self.type = t
        self.name = n


class Data:
    def __init__(self, dtype="?", timestamp=None, initialFrame=None,
                 origin=None, values=None):
        """
        Data encapsulate data. It contains the type, raw data,
        cooked data, origin and time stamp.
        """
        self.type = dtype  # str : Data type
        self.valid = None  # bool : Validité
        self.timestamp = timestamp  # time of data (time when received)
        self.initialFrame = initialFrame  # str :
        self.origin = origin  # str : Id of file or syst. of origin
        self.values = values  # dict :  converted values

    def head4log(self, sep = ' ') -> str :
        time_struct = time.localtime(self.timestamp)
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time_struct)
        s = time_str + sep + self.type + sep + self. origin
        return s

    def str4log(self, sep =  ' ') -> str :
        s = self.head4log(sep) + sep + str(self.values)
        return s

def __str__(self):
    return self.timestamp + '\t' + self.provenance + '\t' + self.originalFrame


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


class dataAPCommand(Data):
    def __init__(self, timeStamp, provenance, originalFrame):
        super().__init__("APCMD", timeStamp, provenance, originalFrame)
        self.command = originalFrame
        print("--> (1) :", self)

    def str4log(self, sep=' ') -> str:
        print ("--> (2) :", self)
        s = super().head4log(sep)# + sep + self.command
        return s

class dataAttitude(Data):
    """
    Attitude of the ship including heading, roll and pitch
    """
    def __init__(self, timestamp, origin, initialFrame, splittedFrame):
        """
        Initialization
        """
        super().__init__("ATTITUDE", timestamp, initialFrame, origin)
        try:
            self.heading = float(splittedFrame[1])
            self.pitch = float(splittedFrame[2])
            self.roll = float(splittedFrame[3])
            self.valid = True
            pass
        except:
            self.heading = None
            self.roll = None
            self.pitch = None
            self.valid = False
            pass
        finally:
            pass

    def str4log(self, sep=' ') -> str:
        s = super().head4log(sep) + sep + f"{self.heading}{sep}{self.roll}{sep}{self.pitch}"
        return s


def dataDecode(timeStamp, orig, frame: str) -> Data:
    #print(f"Trame : {int(timeStamp)} origine \"{orig}\" \"{frame}\"")
    # ts = time.time()

    d = dataDecodeNMEA0183(timeStamp, orig, frame)
    if d is not None: return d

    s = frame.split()
    if len(s) > 1:
        if s[0] == "HDG/M":
            print("Data : cap")
            val = float(s[1])

            dataH = Data("HDG/M", timeStamp, frame, "Nauteff/AP",
                         {"Heading/Mag": val})
            return dataH

        if s[0] == "ATTITUDE":
            return dataAttitude(timeStamp, orig, frame, s)

    d = Data()
    d.timestamp = timeStamp
    d.origin = orig
    d.initialFrame = frame
    d.type = "?"
    d.values = None
    return d


def dataDecodeNMEA0183(timeStamp, orig, frame):
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
