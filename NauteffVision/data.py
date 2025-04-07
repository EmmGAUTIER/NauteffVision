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

import threading
from abc import abstractmethod  # Abstract methods
from datetime import datetime


class DataInterface(threading.Thread):
    def __init__(self, config, queue_out) -> None:
        super().__init__()
        self.config = config
        self.list_out_types = []
        self.list_in_types = []
        self.ready = False
        self.queue_out = queue_out
        return

    def set_queue(self, queue_out) -> None:
        self.queue_out = queue_out
        return

    @abstractmethod
    def put_data(self, data):
        return 0

    @abstractmethod
    def get_data_list_in(self) -> list:
        return []

    @abstractmethod
    def get_data_list_out(self) -> list:
        return []

    @abstractmethod
    def terminate(self) -> None:
        return

    @abstractmethod
    def run(self) -> None:
        pass


class Data:
    """
    Data used by NauteffVision are stored in classes that inherit from this Data.
    It is meant to store a raw frame, its origin, its type, a timestamp and cooked data.
    """
    def __init__(self, dtype="?", timestamp=None, initialFrame=None,
                 origin=None, values=None):
        """
        Creates a new data with raw data, converts them and adds data management
        """
        self.type = dtype  # str : Data type
        self.valid = None  # bool : Validité
        self.timestamp = timestamp  # time of data (time when received)
        self.initialFrame = initialFrame  # str :
        self.origin = origin  # str : Id of file or syst. of origin
        self.values = values  # dict :  converted values

    def get_timestamp(self):
        return self.timestamp

    def head4log(self, sep=' ') -> str:
        """
        Returns a string representation of a data with timestamp, type and raw data
        The string doesn't contain cooked data.
        The main purpose of the string is to prefix cooked data.
        """
        dt = datetime.fromtimestamp(self.timestamp)
        # time_struct = time.localtime(self.timestamp)
        time_str = dt.strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
        s = time_str + sep + self.type + sep + self.origin
        return s

    def str4log(self, sep=' ') -> str:
        """
        Simple and naive representation of a data.
        This function should be overloaded byb inherited classes.
        """
        s = self.head4log(sep) + sep + str(self.values)
        return s

    def __str__(self):
        """
        Another string conversion
        """
        return str(self.timestamp) + '\t' + self.origin + '\t' + self.initialFrame

    def get_initialFrame(self):
        """"
        returns the original data
        """
        return self.initialFrame


class dataNMEA0183(Data):
    def __init__(self, timeStamp, provenance, originalFrame):
        super().__init__(timeStamp, provenance, originalFrame)
        self.type = "NMEA0183"


class dataDPT(dataNMEA0183):
    def __init__(self, timeStamp, provenance, originalFrame):
        super().__init__(timeStamp, provenance, originalFrame)
        self.type = "DPT"
        self.depth = 0.
        self.offset = 0.


class DataSysTime(Data):
    def __init__(self, time_stamp, origin):
        # super().__init__(timeStamp, "SYS", "")
        super().__init__(dtype="SysTime", timestamp=time_stamp, initialFrame="", origin=origin, values=time_stamp)
        self.type = "SysTime"


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
        print("--> (2) :", self)
        s = super().head4log(sep)  # + sep + self.command
        return s


class dataLog(Data):
    user_text: str

    def __init__(self, timestamp, provenance, user_text):
        super().__init__("DashBoard", timestamp, provenance, user_text)
        self.user_text = user_text

    def str4log(self, sep=' ') -> str:
        s = super().head4log(sep) + sep + self.user_text
        return s


class DataWind(Data):
    """
    Wind speed and direction
    """

    def __init__(self, timestamp, origin, initialFrame, splittedFrame):
        """
        Initialization
        """
        super().__init__("WIND", timestamp, initialFrame, origin)
        try:
            self.direction = float(splittedFrame[1])
            self.speed = float(splittedFrame[2])
            self.valid = True
            pass
        except:
            self.speed = None
            self.direction = None
            self.valid = False
            pass
        finally:
            pass

    def str4log(self, sep=' ') -> str:
        s = super().head4log(sep) + sep + f"{self.speed}{sep}{self.direction}"
        return s

    def get_speed(self):
        return self.speed

    def get_direction(self):
        return self.direction


class DataAttitude(Data):
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

    def get_heading(self):
        return self.heading

    def get_pitch(self):
        return self.pitch

    def get_roll(self):
        return self.roll


def dataDecode(timeStamp, orig, frame: str) -> Data:
    # print(f"Trame : {int(timeStamp)} origine \"{orig}\" \"{frame}\"")
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
            return DataAttitude(timeStamp, orig, frame, s)

        if s[0] == "WIND":
            return DataWind(timeStamp, orig, frame, s)

    d = Data()
    d.timestamp = timeStamp
    d.origin = orig
    d.initialFrame = frame
    d.type = "?"
    d.values = None
    return d

class NotNMEA0183(Exception):
    """
    Frame format is not NMEA0183
    """

class NMEA0183ChecksumError(Exception):
    """
    NMEA0183 frame with checksum error
    """
def dataDecodeNMEA0183(timeStamp, orig, frame):

    d = None
    l = len(frame)


    try :
        # check : length
        if l < 10 or l > 82:
            raise NotNMEA0183

        # Terminating <CR> and <LF> are meaningless, so they are removed for decoding
        if frame[l - 1] == '\n' or frame[l - 1] == '\r':
            l = l - 1
        if frame[l - 1] == '\n' or frame[l - 1] == '\r':
            l = l - 1

        # Frames we decode start with a $ sign and have a * before checksum,
        # so check them
        # Some NMEA0183 start with a !
        if frame[0] != "$":
            raise NotNMEA0183("Does not start with $")
        if frame[l-3] != '*':
            raise NotNMEA0183("Does not have a * before checksum")

        payload = frame[1: l-3]

        # Checksum
        checksum = frame[l - 2: l]
        print("checksum : ", checksum)

        csum = 0
        for c in payload:
            csum ^= ord(c)
        # print (f"<{payload}>")
        # print (f"  {csum:02X} {checksum}")
        if  f"{csum:02X}" != checksum:
            raise NMEA0183ChecksumError


    except NotNMEA0183:
        print (f"N'est pas une trame NMEA bien formée")
        pass

    except Exception: # System mustn't crash if an unexpected exception is thrown
        pass


    checksum = frame[l - 3: l]
    print("checksum : ", checksum)
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
