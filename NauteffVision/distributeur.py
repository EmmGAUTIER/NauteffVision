"""
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
"""

import queue
import inputfiles
import outputfiles
import dashboard
import tocante

class DataType:
    def __init__(self, id):
        self.Id = id
        pass


dataTypes = []

class DataListener:
    def __init__(self):
        pass

    def getListenedDataTypes(self):
        return []


class DataEmitter:
    def __init__(self):
        pass

    def getEmittedDataTypes(self):
        return []


class Distributeur:
    """
    Le Distributeur reçoit des données, les distribue aux instruments
    du tableau de bord ou Listeners et les envoie vers les fichiers.
    Les Listensers sont les instruments et modules de calculs.
    Les fichiers sont les fichiers au sens unix (disque, tubes, ...).
    Le distributeur ne réalise pas de traitement.
    """

    def __init__(self, config):

        # Création des objets
        self.MainQueue = queue.Queue() # Create the queue to receive datas
        self.inputFiles = inputfiles.InputFiles(config["ios"], self.MainQueue)
        self.dashboard = dashboard.DashBoard(config["dashboard"], self.MainQueue)
        self.outputFiles = outputfiles.OutputFiles(config["ios"], self.MainQueue)
        self.tocante = tocante.Tocante(self.MainQueue)

        self.dataListeners = []
        self.dataListeners.append(self.dashboard)
        self.dataListeners.append(self.outputFiles)

        # Activation des objets
        print (" ===> 1")
        self.tocante.start()
        print (" ===> 2")
        self.inputFiles.start()
        print (" ===> 3")
        self.dashboard.start()
        print (" ===> 4")

        print("Distributeur : Début de boucle")
        while True:
            data = self.MainQueue.get(timeout=1.0)
            self.outputFiles.putData(data)
            print("Type de donnée reçue : ", data.type)
            for l in self.dataListeners:
                l.putData(data)


