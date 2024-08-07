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

# from os import open
import os
import selectors
import threading
import time
import data

class ios(threading.Thread):
    """
    ios manages the inputs and outputs of data. It runs whitin a thread.
    Data come from files and are send to files.
    The files may be devices such as ttys or
    named pipes. 
    ios listen one or more files and send data to a queue
    """
    def __init__(self, cfg, q):
        """
        Initialise the ios. cfg is the "ios" section of the json config file.
        ios opens each file in non blocking mode and initiates a selector on files.
        q is the queue to send data. 
        """
        super().__init__()
        self.fds = []
        self.ids = []
        self.labels = []
        self.sel = selectors.DefaultSelector() # 
        self.queue = q  # Queue for messages to send

        for io in cfg:
            print("IO : ", io["file"])
            o_mode = os.O_NONBLOCK
            if "direction" in io:
                direction = io["direction"]
            else:
                direction = "in"
            if direction == "in":
                o_mode = o_mode | os.O_RDONLY
            elif direction == "out":
                o_mode = o_mode | os.O_WRONLY | os.O_APPEND | os.O_CREAT
            elif direction == "inout":
                o_mode = o_mode | os.O_RDONLY | os.O_WRONLY | os.O_APPEND | os.O_CREAT
            else:
                return
            fd = os.open(io["file"], o_mode)
            f = open(fd, "r")
            self.fds.append(f)
            self.ids.append(io["id"])
            self.labels.append(io["label"])
            if direction in ("in", "inout"):
                self.sel.register(f, selectors.EVENT_READ)

    def sendData(self, d):
        # print ("Donnée ", d)
        pass

    def run(self):
        """
        Runs in a thread. It listens the files. When data is available
        from a file it reads it, decodes it puts a timestamp (system time)
        and send it to the main queue.
        """
        while True:
            events = self.sel.select()
            for file, mask in events:
                # event should be selectors.EVENT_READ, so let's read
                line = file.fileobj.readline()
                ts = time.time()
                # print(l)
                num = self.fds.index(file.fileobj)
                org = self.ids[num] + "," + self.labels[num]
                d = data.dataDecode(ts, org, line)
                self.queue.put(d)
