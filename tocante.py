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

import queue
import time
import threading
# from math import floor
import math
import data

class Tocante(threading.Thread):
    """ A clock that sends time tics to a queue """

    def __init__(self, q):
        super().__init__()
        self.queue = q
        # self.msec = 100

    def run(self):
        while True:
            t = time.time()
            t = math.floor(10 * t)
            t = t / 10
            
            dt = time.gmtime(t)
            dt = time.localtime()
            
            toc = data.Data("SysTime", t, str(t), "SYS",
                            {"Time": t,
                             "Year": dt.tm_year,
                             "Month": dt.tm_mon,
                             "Day": dt.tm_mday,
                             "Hour": dt.tm_hour,
                             "Minute": dt.tm_min,
                             "Second": dt.tm_sec,
                             "WeekDay": dt.tm_wday})
            self.queue.put(toc)
            
            nextt = t + 0.1
            time.sleep(nextt - time.time())
