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
import ios
import dashboard
import tocante
import datasimulator
#import time
#import data


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
        self.queue = queue.Queue() # Create the queue to receive datas
        self.fileInputs = ios.ios(config["ios"], self.queue)
        self.fileOutputs = None #ios.ios(config["ios"], self.queue)
        self.dashboard = dashboard.DashBoard(config)
        self.tocante = tocante.Tocante(self.queue)
        #self.simulator = datasimulator.DataSimulator_i(self.queue)
        
        # List of data listeners and data emitters
        self.listeners = self.dashboard.instruments
        self.emitters = []

        # Activation des objets
        self.tocante.start()
        self.fileInputs.start()
        self.dashboard.start()
        #self.simulator.start()

        print("Distributeur : Début de boucle")
        while True:
            d = self.queue.get(timeout=1.0)
            self.fileInputs.sendData(d)
            #print("--------------------------------------------------------")
            #print("Type de donnée reçue : ", d.type)
            for l in self.listeners :
                #print("  --: ", l.get_data_list_in())
                if d.type in l.get_data_list_in() :
                    #print (":::: ", l)
                    l.put_data(d)
            
                    
