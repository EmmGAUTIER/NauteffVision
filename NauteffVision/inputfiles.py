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

class InputFiles(threading.Thread):
    """
    ios manages the inputs and outputs of data. It runs whitin a thread.
    Data come from files and are send to files.
    The files may be devices such as ttys or
    named pipes. 
    ios listen one or more files and send data to a queue
    """
    def __init__(self, pConfig, pQueue):
        """
        Initialise the ios. cfg is the "ios" section of the json config file.
        ios opens each file in non blocking mode and initiates a selector on files.
        q is the queue to send data. 
        """
        super().__init__()
        self.pipe = os.pipe()
        self.fds = []     # File descriptors
        self.ids = []     # Identifiers of files 
        self.labels = []  # File labels
        self.selector = selectors.DefaultSelector() # 
        self.queue = pQueue  # Queue for messages to send

        for io in pConfig:
            try :
                fileName = io["file"]
                #print ("Fichier : ", fileName)
                fileDirection = io["direction"]
                fileDTypes = io.get("dtypes")
                fileFormat = io.get("format")
                fileLabel = io.get("label")
                fileId = io.get("id")
                # L'ouverture d'un tube nommé bloque sans l'option os.O_NONBLOCK
                # File has to be first opened with os.open and this flag,
                # and after with builin function open
                if fileDirection == "in":
                    df = os.open(fileName, os.O_RDONLY | os.O_NONBLOCK)
                    fileHandler = open (df, "rt")
                    print ("Ouvert : ", fileName)
                    self.fds.append(fileHandler)
                    self.ids.append(io["id"])
                    self.labels.append(io["label"])
                    self.selector.register(fileHandler, selectors.EVENT_READ)                

            except Exception as e:
                print(f"Exception : '{e.args[0]}'")
            except KeyError as e:
                print(f"KeyError: Description de fichier : la rubrique '{e.args[0]}' est manquante.")
            finally:
                pass

    def run(self):
        """
        Runs in a thread. It listens the files. When data is available
        from a file it reads it, decodes it puts a timestamp (system time)
        and send it to the main queue.
        """
        while True:
            events = self.selector.select()
            for file, mask in events:
                """
                if file == self.pipe :
                    if file.fileobj.readline() == "Terminate":
                        self.closeFiles()
                        return
                """
                # event should be selectors.EVENT_READ, so let's read
                line = file.fileobj.readline()
                ts = time.time()
                # print(l)
                num = self.fds.index(file.fileobj)
                org = self.ids[num] + "," + self.labels[num]
                d = data.dataDecode(ts, org, line)
                self.queue.put(d)

    def closeFiles ():
        """
        Close all input files when terminating
        """
        print ("Fermeture des fichiers")
        for file in self.fds:
            file.close()
        pass

    def terminate(self) :
        self.pipe.write("Terminate\n")
        pass