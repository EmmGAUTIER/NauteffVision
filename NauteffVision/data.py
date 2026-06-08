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
import math
from abc import abstractmethod  # Abstract methods
from datetime import datetime


class DataInterface(threading.Thread):
    """
    An abstract class for files, devices and compute modules

    """
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

    def __init__(self, dtype="?", timestamp=None, origin=None, initial_frame=None, split_frame=None):
        """
        Creates a new data with raw data, converts them and adds data management.
        This function does the general initialization of data without decoding it.
        It has to be called by derived classes of Data upon on creation.
        dtype : str Type of data
        timestamp : date and time of creation or reception of data
        origin : origin of data, name of the stream, file...
        initialFame : initial string containing original data to be decoded
        split_frame : frame split in fields, separator is white space
        """
        self.type = dtype                   # str : Data type
        self.valid = False                  # bool : Validité
        self.timestamp = timestamp          # time of data (time when received)
        self.initial_frame = initial_frame  # str :
        self.origin = origin                # str : Id of file or syst. of origin
        self.split_frame = split_frame      # fields of frame, separated by blanks

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
        s = time_str + sep + self.origin + sep + self.type
        return s

    def str4log(self, sep=' ') -> str:
        """
        Simple and naive representation of a data.
        This function should be overloaded by inherited classes.
        """
        return  self.head4log(sep) + sep + str(self.initial_frame)

    def __str__(self):
        """
        Another string conversion
        """
        try :
            s = str(self.timestamp) + '\t' + self.origin + '\t' + self.initial_frame
        except:
            s = "Erreur Décodage "

        return s

    def get_initialFrame(self):
        """"
        returns the original data
        """
        return self.initial_frame


class dataNMEA0183(Data):
    def __init__(self, timeStamp, provenance, originalFrame):
        super().__init__(timeStamp, provenance, originalFrame)
        self.type = "NMEA0183"


class dataDPT(dataNMEA0183):
    def __init__(self, timeStamp, origin, original_frame, split_frame=None):
        # split_frame ignored by dataDPT
        super().__init__(timeStamp, origin, original_frame)
        self.type = "DPT"
        self.depth = 0.
        self.offset = 0.


class DataSysTime(Data):
    def __init__(self, time_stamp, origin):
        # systime has no frame and no split_frame, it uses only time stamp
        super().__init__("SysTime", time_stamp, origin, "")
        self.type = "SysTime"


"""
class dataNauteff(Data):
    def __init__(self, timeStamp, provenance, originalFrame):
        super().__init__(timeStamp, provenance, originalFrame)

class dataHeading(Data):
    def __init__(self, timeStamp, origin, original_frame, split_frame):
        super().__init__(timeStamp, origin, original_frame, split_frame)
        originalFrame.split()

        self.heading = int(originalFrame)
"""

class DataMotorException(Exception):
    """
    Exception used by DataMotor when an error occurs
    """
    pass

class DataMotor(Data):
    """
    Message from autopilot, containing motor and clutch information
    Status of motor and clutch have to be kept other vars.
    """

    CLUTCH_ENGAGE    =  1
    RUN_PORT         =  2
    RUN_STARBOARD    =  3
    ADC_VALUES       =  4
    MOVE_REPORT      =  5
    STALLED          = 16
    STOPPING         = 17
    STOPPED          = 18
    CLUTCH_DISENGAGE = 19
    ESTIMATED_ANGLE  = 21

    def __init__(self, timeStamp, origin, original_frame, split_frame):
        super().__init__("MOTOR", timeStamp, origin, original_frame, split_frame)
        s = self.split_frame[0:3]
        #print (f"Décodage trame moteur {s}")
        self.message_type = None  # several message types from motor
        self.valid = False
        self.timeToMove = None
        self.helmAngle = None
        self.message_type = None
        try :
            if self.split_frame == ["MOTOR", "LL", "run", "to", "port"] :
                self.message_type = DataMotor.RUN_PORT

            if self.split_frame == ["MOTOR", "LL", "run", "to", "starboard"] :
                self.message_type = DataMotor.RUN_STARBOARD

            if self.split_frame == ["MOTOR", "LL", "stop"] :
                self.message_type = DataMotor.STOPPING

            if self.split_frame == ["MOTOR", "LL", "engage", "tiller"]:
                self.message_type = DataMotor.CLUTCH_ENGAGE

            if self.split_frame == ["MOTOR", "LL", "disengage", "tiller"]:
                self.message_type = DataMotor.CLUTCH_DISENGAGE

            if self.split_frame == ["MOTOR", "overcurrent", "stop"]:
                self.message_type = DataMotor.STALLED

            if self.split_frame == ["MOTOR", "stopping"] :
                self.message_type = DataMotor.STOPPING

            if self.split_frame == ["MOTOR", "end", "moving", "time"]:
                self.message_type = DataMotor.STOPPING

            if self.split_frame == ["MOTOR", "stalled", "stop"]:
                self.message_type = DataMotor.STALLED

            if self.split_frame == ["MOTOR", "stalled"]:
                self.message_type = DataMotor.STALLED

            if self.split_frame[0: 3] ==  ['MOTOR', 'estimated', 'angle'] :
                self.helmAngle = float(self.split_frame[3])
                self.message_type = DataMotor.ESTIMATED_ANGLE
                #print (f"@@@@@@@@@@@@      Position estimée de la barre : {self.helmAngle*(180./math.pi):+6.1f}")
                pass

            if self.split_frame[0 : 3] == ["MOTOR", "move", "time"]:
                self.timeToMove = float(self.split_frame[3])
                if self.timeToMove > 0:
                    self.message_type = DataMotor.RUN_STARBOARD
                else:
                    self.message_type = DataMotor.RUN_PORT

            if self.split_frame == ["MOTOR", "end", "moving", "time"] :
                self.message_type = DataMotor.STOPPED

            if self.message_type is not None:
                self.valid = True
            pass

        except DataMotorException:
            self.valid = False
            print ("########        Erreur décodage trame moteur")
        except:
            self.valid=False
            print ("########        Erreur décodage trame moteur")
        finally:
            pass


    def get_helm_estimated_pos(self):
        return None

class dataAPPID(Data):
    """
    Autopilot informations
    Type identifier : AP_PID
    """
    def __init__(self, timeStamp, origin, original_frame, split_frame):
        super().__init__("AP_PID", timeStamp, origin, original_frame, split_frame)

        self.hdg = None
        self.hdg_gap = None
        self.hdg_int_gap = None
        self.hdg_der_gap = None
        self.steer_request = None

        try:
            # TODO use self.split_frame instead of fields
            fields = original_frame.split()
            #print("Fields :")
            #for i in range(2, 7):
            #    print(f"PID field[{i}] = {fields[i]}")
            self.hdg = float(fields[2])
            self.hdg_gap = float(fields[3])
            self.hdg_int_gap = float(fields[4])
            self.hdg_der_gap = float(fields[5])
            self.steer_request = float(fields[6])
            self.valid = True
            #print(f"heading requested  = {self.hdg*(180./math.pi):+7.2f} deg.")
            #print(f"PID gap            = {self.hdg_gap*(180./math.pi):+7.2f} deg.")
            #print(f"PID integrated gap = {self.hdg_int_gap*(180./math.pi):+7.2f} deg.")
            #print(f"PID derived gap    = {self.hdg_der_gap*(180./math.pi):+7.2f} deg.")
            #print(f"Steer request      = {self.steer_request*(180./math.pi):+7.2f} deg.")

        except:
            self.hdg = None
            self.hdg_gap = None
            self.hdg_int_gap = None
            self.hdg_der_gap = None
            self.steer_request = None
            self.valid = False

        finally:
            pass

    def get_hdg(self):
        return self.hdg

    def get_hdg_gap(self):
        return self.hdg_gap

    def get_hdg_int_gap(self):
        return self.hdg_int_gap

    def get_hdg_der_gap(self):
        return self.hdg_der_gap

class dataAPCommand(Data):
    def __init__(self, timeStamp, origin, original_frame, split_frame):
        super().__init__("APCMD", timeStamp, origin, original_frame, split_frame)
        self.command = original_frame
        # print("--> (1) :", self)

    def str4log(self, sep=' ') -> str:
        # print("--> (2) :", self)
        s = super().head4log(sep)  # + sep + self.command
        return s


class dataLog(Data):
    user_text: str

    def __init__(self, timestamp, origin, initial_frame):
        super().__init__("DashBoard", timestamp, origin, initial_frame)
        self.user_text = initial_frame

    def str4log(self, sep=' ') -> str:
        s = super().head4log(sep) + sep + self.user_text
        return s


class DataWind(Data):
    """
    Wind speed and direction
    """

    def __init__(self, timestamp, origin, initial_frame, split_frame):
        """
        Initialization
        """
        super().__init__("WIND", timestamp, origin, initial_frame, split_frame)
        try:
            self.direction = float(split_frame[1])
            self.speed = float(split_frame[2])
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

    def __init__(self, timestamp, origin, initial_frame, split_frame):
        """
        Initialization
        """
        super().__init__("ATTITUDE", timestamp, origin, initial_frame, split_frame)
        try:
            self.roll = float(split_frame[1])
            self.pitch = float(split_frame[2])
            self.heading = float(split_frame[3])
            self.yawrate = float(split_frame[4])
            self.valid = True
            pass
        except:
            self.heading = None
            self.roll = None
            self.pitch = None
            self.yawrate = None
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

    def get_yawrate(self):
        return self.yawrate


def dataDecode(timeStamp, orig, frame: str) -> Data:
    # print(f"Trame : {int(timeStamp)} origine \"{orig}\" \"{frame}\"")
    # ts = time.time()

    # d = dataDecodeNMEA0183(timeStamp, orig, frame)
    # if d is not None:
    #    return d

    # TODO convert to if ... elif ... elif .....
    s = frame.split()
    if len(s) > 1:

        if s[0] == "AP" and s[1] == "PID":
            return dataAPPID(timeStamp, orig, frame, s)

        if s[0] == "MOTOR":
            return DataMotor(timeStamp, orig, frame, s)


        if s[0] == "ATTITUDE":
            return  DataAttitude(timeStamp, orig, frame, s)


        #if s[0] == "WIND":
        #    return DataWind(timeStamp, orig, frame, s)


    d = Data("?", timeStamp, orig, frame, s)
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
    """
    NMEA 0183 frame decoding, work in progress
    """
    d = None
    l = len(frame)

    try:
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
        if frame[l - 3] != '*':
            raise NotNMEA0183("Does not have a * before checksum")

        payload = frame[1: l - 3]

        # Checksum
        checksum = frame[l - 2: l]
        # print("checksum : ", checksum)

        csum = 0
        for c in payload:
            csum ^= ord(c)
        # print (f"<{payload}>")
        # print (f"  {csum:02X} {checksum}")
        if f"{csum:02X}" != checksum:
            raise NMEA0183ChecksumError


    except NotNMEA0183:
        # print (f"N'est pas une trame NMEA bien formée")
        pass

    except Exception:  # System mustn't crash if an unexpected exception is thrown
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
        # d.type = "DPT"
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
