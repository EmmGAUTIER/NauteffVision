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

import os
# import queue
import selectors
import threading
import time
import data


class DataFile(data.DataInterface):
    def __init__(self, config, queue_out):
        super().__init__(config, queue_out)

        self.filename = config.get("filename")
        self.dtypes = config.get("dtypes")
        self.id = config.get("id")
        self.direction = config.get("direction")
        self.rawmode = True if config.get("raw") else False
        self.ready = False

        mode = "rt" if (self.direction == "in") else "at"
        print(f"Ouverture de : {self.filename}")
        self.file = open(self.filename, mode)
        print(f"Résultat     : {self.file.fileno()} ")
        if mode == "at" :
            self.file.write("*****  NauteffVision Start  *****\n")

        return

    def get_data_list_in(self) -> list:
        # do not listen
        return []

    def get_data_list_out(self) -> list:
        return "all"

    def run(self) -> None:
        end_loop = False
        self.ready = True
        if self.direction == "in":
            while  not self.file.closed:
                try:
                    line = self.file.readline()
                    # print(f"Ligne : {line}")
                    ts = time.time()
                    d = data.dataDecode(ts, self.id, line)
                    # print (f"Type de donnée : {d.type}")
                    self.queue_out.put(d)
                except ValueError:
                    print(f"Erreur IO {self.filename}")
                finally:
                    # self.file.close()
                    pass


    def put_data(self, data):
        res = -1
        if self.ready:
            if (self.direction == "out") and (self.dtypes == "all" or data.type == self.dtypes):
                if self.rawmode is True:
                    res = self.file.write(data.get_initialFrame() + '\n')
                else:
                    res = self.file.write(data.str4log() + '\n')
                self.file.flush()
        return res

    def terminate(self) -> None:
        self.ready = False
        self.file.close()
        print ("DataFile.terminate() : ", self.filename)
        return


class DataFile_bis(data.DataInterface):

    def __init__(self, config, queue_out, ):
        super().__init__(config, queue_out)

        self.filename = config.get("filename")
        self.dtypes = config.get("dtypes")
        self.id = config.get("id")
        self.direction = config.get("direction")
        if config.get("raw") == 1:  # may be None no [] but .get() instead
            self.rawmode = True
        else:
            self.rawmode = False

        # self.queue_file = queue.Queue()  # queue.Queue(maxsize=100)

        # selector is used to wait for incoming data and message data
        # message data are used to control FileInput
        # and especially terminate it when receiving "STOP"
        # register data ready to read from file
        # and message to read from pipe
        self.selector = selectors.DefaultSelector()

        # Ouverture du fichier en écriture, puis en lecture, ajout à selector
        # When reading from a named pipe if no reader has opened the pipe
        # for writing the builtin open block, so we have to open for reading
        # and writing and with O_NDELAY with os.open and the use builtin open
        # twice, for reading and for writing.
        if self.direction == "in":
            self.file_bis = os.open(self.filename, os.O_RDONLY | os.O_NDELAY)
            self.file_in = open(self.file_bis, "rt")
            self.selector.register(self.file_in, selectors.EVENT_READ)
            self.file_out = None
        else:
            self.file_bis = os.open(self.filename, os.O_WRONLY | os.O_NDELAY | os.O_CREAT)
            self.file_out = open(self.file_bis, "at")
            self.file_in = None

        # Création du tube de comm avec pipe et ajout à selector
        self.msg_pipe = os.pipe()  # tuple : (reading file , writing file)
        self.selector.register(self.msg_pipe[0], selectors.EVENT_READ)

        return

    def put_data(self, data):
        res = 0
        if self.ready:
            if (self.direction == "out") and (self.dtypes == "all" or data.type == self.dtypes):
                if self.rawmode is True:
                    res = self.file_out.write(data.get_initialFrame() + '\n')
                else:
                    res = self.file_out.write(data.str4log() + '\n')
                self.file_out.flush()
        return res

    def get_data_list_in(self) -> list:
        # do not listen
        return []

    def get_data_list_out(self) -> list:
        return "all"

    def run(self) -> None:
        end_loop = False
        self.ready = True

        while not end_loop:
            events = self.selector.select(None)
            for file, mask in events:
                # print(f"Événement  : fichier = {file} / {file.fd}, event = {mask}")
                if file.fd == self.msg_pipe[0]:
                    line = os.read(self.msg_pipe[0], 1000)
                    print(f"------> InputFile : message reçu {line} ")
                    if line == b"Terminate\n":
                        # TODO : Fermeture des fichiers
                        # self.file_in.close()
                        # self.file_out.close()
                        os.close(self.file_bis)
                        os.close(self.msg_pipe[0])
                        os.close(self.msg_pipe[1])
                        # print ("------->>> Fermeture des fichiers demandée")
                        end_loop = True
                elif file.fd == self.file_in.fileno():
                    line = self.file_in.readline()
                    ts = time.time()
                    # print(f"FileInput lecture de : {line}")
                    d = data.dataDecode(ts, self.id, line)
                    self.queue_out.put(d)

        return

    def terminate(self) -> None:
        res = os.write(self.msg_pipe[1], b"Terminate\n")
        return


class InputFiles_old(threading.Thread):
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
        self.fds = []  # File descriptors
        self.ids = []  # Identifiers of files
        self.labels = []  # File labels
        self.selector = selectors.DefaultSelector()  #
        self.queue = pQueue  # Queue for messages to send

        for id, io in pConfig.items():
            try:
                fileName = io["file"]
                # print ("Fichier : ", fileName)
                fileDirection = io["direction"]
                fileDTypes = io.get("dtypes")
                fileFormat = io.get("format")
                fileLabel = io.get("label")
                # fileId = io.get("id")
                fileID = id
                # L'ouverture d'un tube nommé bloque sans l'option os.O_NONBLOCK
                # File has to be first opened with os.open and this flag,
                # and after with builin function open
                if fileDirection == "in":
                    df = os.open(fileName, os.O_RDONLY | os.O_NONBLOCK)
                    fileHandler = open(df, "rt")
                    # print("Ouvert : ", fileName)
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
                # print(f"FileInput lecture de : {line}")
                num = self.fds.index(file.fileobj)
                org = self.ids[num]  # + "," + self.labels[num]
                d = data.dataDecode(ts, org, line)
                self.queue.put(d)

    def closeFiles(self):
        """
        Close all input files when terminating
        """
        print("Fermeture des fichiers")
        for file in self.fds:
            file.close()
        pass

    def terminate(self):
        # self.pipe.write("Terminate\n")
        self.closeFiles()
        pass
