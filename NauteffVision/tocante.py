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

# from math import floor
import math
import threading
import time
import data


class Tocante(data.DataInterface):
    """ A clock that sends time tics every second to a queue """

    def __init__(self, config, queue_out):
        super().__init__(config, queue_out)
        self._stop_event = threading.Event()
        return

    def put_data(self, data):
        # Nothing to do with data
        return 0

    def get_data_list_in(self) -> list:
        # Nothing to do with data
        return []

    def get_data_list_out(self) -> list:
        return ["SYS"]

    def run(self):
        while not self._stop_event.is_set():
            t = time.time()

            t = math.floor(10 * t)
            t = t / 10

            """

            # dt = time.gmtime(t)
            dt = time.localtime()

            toc = data.DataSysTime("SysTime", t, str(t), "SYS",
                            {"Time": t,
                             "Year": dt.tm_year,
                             "Month": dt.tm_mon,
                             "Day": dt.tm_mday,
                             "Hour": dt.tm_hour,
                             "Minute": dt.tm_min,
                             "Second": dt.tm_sec,
                             "WeekDay": dt.tm_wday})
            self.queue_out.put(toc)
            
            """
            ts = data.DataSysTime(t, origin = "Tocante")
            self.queue_out.put(ts)

            # print(f"----> Tocante : tic {ts}") # used for debugging only

            next_tic = t + 1.0
            self._stop_event.wait(next_tic - time.time())
        return

    def terminate(self) -> None:
        self._stop_event.set()
