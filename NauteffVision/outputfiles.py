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
import time
import data

class OutputFile():
    def __init__(self, config):
        try :
            self.filename = config["file"]
            self.format = config["format"]
            self.id = config["id"]
            self.label = config.get("label")
            self.fd = os.open(self.fileName, os.O_WRONLY | os.O_NONBLOCK)
            # fileHandler = open (df, "wt")
            print ("Ouvert : ", self.filename)

        except Exception as e:
            print(f"Error lors de l'ouverture de {self.filename} '{e.args[0]}'")
        except KeyError as e:
            print(f"KeyError: Description de fichier : la rubrique '{e.args[0]}' est manquante.")
        finally:
            pass


    def putData (self, data) :
        try :
            self.write(data.str())
        except Exception as e:
            print(f"'{e.args[0]}'")
        finally:
            pass

        return

 
class OutputFiles():
    """
    OutputFile outputs data to files.
    Data come from the Distributeur.
    OutputData filters data.
    The files may be devices such as ttys or named pipes.
    OutputFile doesn't run in a thread.
    """
    def __init__(self, pConfig, pQueue):
        """
        Initialise the ios. cfg is the "ios" section of the json config file.
        ios opens each file in non blocking mode and initiates a selector on files.
        q is the queue to send data. 
        """
        super().__init__()
        self.fds = []        # File descriptors
        self.ids = []        # Identifiers of files 
        self.labels = []     # File labels
        self.filtertypes = []
        self.queue = pQueue  # Queue for messages to send

        for io in pConfig:
            try :
                fileName = io["file"]
                #print ("Fichier : ", fileName)
                fileDirection = io["direction"]
                fileDTypes = io.get("dtypes")
                #fileFormat = io.get("format") #
                #fileLabel = io.get("label")   #
                fileId = io.get("id")
                # L'ouverture d'un tube nommé bloque sans l'option os.O_NONBLOCK
                # File has to be first opened with os.open and this flag,
                # and after with builtin function open
                if fileDirection == "out":
                    df = os.open(fileName, os.O_WRONLY | os.O_CREAT, mode=0o640)
                    fileHandler = open (df, "wt")
                    print ("Ouvert : ", fileName)
                    self.fds.append(fileHandler)
                    self.ids.append(io["id"])
                    self.labels.append(io["label"])
                    ts = io.get("types")
                    if ts == "all" or ts == None:
                        self.filtertypes.append(None)
                    else:
                        self.filtertypes.append(ts.split(','))

            except Exception as e:
                print(f"Error opening {fileName}'{e.args[0]}'")
            except KeyError as e:
                print(f"KeyError: Description de fichier : la rubrique '{e.args[0]}' est manquante.")
            finally:
                pass

    def putData (self, pData) :
        if pData.origin != "SYS":
            for file, filter in zip (self.fds, self.filtertypes) :
                if filter == None or pData in filter :
                    s = pData.str4log()
                    #print("### outputFile écriture d'une donnée : ", s)
                    file.write(s + '\n')
                    file.flush()
                    #print (s, file=file)
                    os.fsync(file)
        return
 
    def closeFiles (self):
        """
        Close all input files when terminating
        """
        print ("Fermeture des fichiers")
        for file in self.fds:
            file.close()
        pass

    def terminate(self):
        self.closeFiles()
