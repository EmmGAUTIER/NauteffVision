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
import datafile
import dashboard
import tocante
import datasimulator


class Distributeur:
    """
    Le Distributeur reçoit des données, et les distribue aux entités de type
    DataInterface. Ces entités sont des fichiers au sens unix
    (sur disque, tubes, ...), des modules de calcul, et l'interface graphique
    de type DashBoard.
    Lors de sa création, il crée les gestionnaires de fichiers, la tocante
    et l'interface graphique, puis il lance leurs exécutions.
    Il utilise les infos du dictionnaire de configuration et communique hs
    ces informations aux objets créés.
    Il communique en utilisant une queue pour lire les données et en appelant
    la fonction membre put_data() des objets qui dérivent de DataInterface.
    Le distributeur ne réalise pas de traitement.
    """

    def __init__(self, config):
        """
        Initialisation selon indications contenues dans config.
        config est un dictionnaire décrivant les fichiers,
        les calculs et le tableau de bord.
        """
        self.config = config
        # Création des objets
        self.main_queue = queue.Queue()  # Create the queue to receive data
        self.data_interfaces = []

        # DataInterfaces creation

        # tocante la tocante envoie l'heure dans la queue toutes les secondes.
        self.data_interfaces.append(tocante.Tocante(None, self.main_queue))

        if config.get ("demo"):
            # self.data_interfaces.append(datafileDemo)
            pass
        else:
            # Fichiers
            for file_id, file_cfg in config.get("ios").items():
                print(f"Ouverture du fichier {file_id:12s} : {file_cfg.get('filename')}")
                self.data_interfaces.append(datafile.DataFile(file_cfg, self.main_queue))

        # Simulateurs

        self.data_interfaces.append(dashboard.Dashboard(config.get("dashboard"), self.main_queue))

    def loop(self):
        """
        loop ()
        Boucle du distributeur. Démarre toutes les instances DataInterfaces
        lit sur la file les données et les distribue aux instances DataInterfaces.
        Cette boucle se termine par break lorsqu'elle reçoit le message "Terminate"
        Elle arrête alors les DaraInterfaces.
        """
        # Start all data interfaces (which run in threads)
        for di in self.data_interfaces:
            di.start()

        # print("Distributeur : Début de boucle") # Pour mise au point
        # Boucle infinie, sortie par instruction break
        while True:
            data = self.main_queue.get()
            if type(data) == str and data == "Terminate":
                print("Fin détectée")
                break
            # print(data.str4log())
            for di in self.data_interfaces:
                di.put_data(data)

        # End loop , stop all data_interfaces : tocante, dashboard, files, computers
        for di in self.data_interfaces:
            di.terminate()
