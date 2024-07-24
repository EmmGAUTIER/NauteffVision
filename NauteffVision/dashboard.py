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

#import math
import threading
import tkinter
import tkinter.font as tkFont
# from math import sin, cos
# import calculs
#from functools import partial
#import calculs

#import data
#from data import Data, dataAttitude
import instrument as instrument
import data as data
import calculs # import deg2rad
from numpy.distutils.fcompiler import none

class DashBoard(threading.Thread, data.DataListener):

    def __init__(self, config, queue):
        super(DashBoard, self).__init__()
        self.config = config
        self.queue = queue
        self.display_mode = 0
        self.tk = None
        self.fen = None
        self.instruments = []
        self.daycolors = {"back": "white", "fore": "black"}
        self.nightcolors = {"back": "black", "fore": "red"}
        self.backclr = self.daycolors["back"]
        self.foreclr = self.daycolors["fore"]
        self.datahub = None
        self.font_small_normal = None
        self.font_medium_normal = None
        self.font_large_normal = None
        self.font_small_tt = None
        self.font_medium_tt = None
        self.font_large_tt = None
        self.mincellx = None
        self.maxcellx = None
        self.mincelly = None
        self.maxcelly = None
        self.framesize_x = 0
        self.framesize_y = 0
        # self.canvases = []
        self.instruments = []
        self.font_small_normal = None
        self.font_medium_normal = None
        self.font_large_normal = None

    def on_resize(self, event):
        print("--->> on resize")
        return

    def configure_event(self, event):

        #print("--> Évènement :", event)
        #print(f"self.fen.win_info_xx {self.fen.winfo_width()} x {self.fen.winfo_height()}")

        # Trop d'évènements lors d'un redimensionnements
        # il faut tester si il y a un changement de taille
        # Le code suivant au démarrage empèche l'affichage des instruments.
        #if self.framesize_x == self.fen.winfo_width() and self.framesize_y == self.fen.winfo_height() :
        #    #print("====> Pas de changement de taille")
        #    return

        self.framesize_x = self.fen.winfo_width()
        self.framesize_y = self.fen.winfo_height()
        nbcellx = self.maxcellx - self.mincellx + 1
        nbcelly = self.maxcelly - self.mincelly + 1

        self.font_small_normal = tkFont.Font(family="Arial",
                                             size=int((self.framesize_x / nbcellx) * 0.05),
                                             weight="bold",
                                             slant="roman")
        self.font_medium_normal = tkFont.Font(family="Arial",
                                              size=int((self.framesize_x / nbcellx) * 0.1),
                                              weight="bold",
                                              slant="roman")
        self.font_large_normal = tkFont.Font(family="Arial",
                                             size=int((self.framesize_x / nbcellx) * 0.15),
                                             weight="bold",
                                             slant="roman")

        self.font_small_tt = tkFont.Font(family="Courrier",
                                         size=int((self.framesize_x / nbcellx) * 0.05),
                                         weight="bold",
                                         slant="roman")
        self.font_medium_tt = tkFont.Font(family="Courrier",
                                          size=int((self.framesize_x / nbcellx) * 0.1),
                                          weight="bold",
                                          slant="roman")
        self.font_large_tt = tkFont.Font(family="Courrier",
                                         size=int((self.framesize_x / nbcellx) * 0.15),
                                         weight="bold",
                                         slant="roman")

        # event.width
        for instr in self.instruments:
            cvs = instr.icanvas
            # #cvs.configure(width=30, height=30)
            px = int((self.framesize_x * (instr.cellx - self.mincellx)) / nbcellx)
            py = int((self.framesize_y * (instr.celly - self.mincelly)) / nbcelly)
            sx = int((instr.cellsizex * self.framesize_x) / nbcellx)
            sy = int((instr.cellsizey * self.framesize_y) / nbcelly)
            #print (f"px = {px}, py = {py}, sx = {sx}, sy = {sy}")
            cvs.place(x=px, y=py)
            cvs.configure(width=sx, height=sy)
            instr.draw()

        return

    def run(self):
        #print (" ----> Démarrage dashboard : run()")
        self.fen = tkinter.Tk()
        self.fen.title("N A U T E F F")
        self.fen.geometry("640x480")
        self.fen.bind('<Configure>', self.configure_event, add=None)
        #self.fen.bind('<Configure>', self.configure_event, add=None)

        for cfginstr in self.config["instruments"]:
            # print(cfginstr["type"], cfginstr["cell_origx"], cfginstr["cell_origy"], cfginstr["cell_width"],
            #       cfginstr["cell_height"])
            cx = int(cfginstr["cell_origx"])
            cy = int(cfginstr["cell_origy"])
            lx = int(cfginstr["cell_width"])
            ly = int(cfginstr["cell_height"])

            inst = instrument.Instrument.create_instrument(self, cfginstr)
            self.instruments.append(inst)
            cnvs = tkinter.Canvas(self.fen, width=1, height=1)
            inst.setcanvas(cnvs)
            inst.set_colors(self.daycolors)

            if self.mincellx is None:
                self.mincellx = cx
                self.maxcellx = cx + lx - 1
                self.mincelly = cy
                self.maxcelly = cy + ly - 1
            else:
                self.mincellx = min(self.mincellx, cx)
                self.mincelly = min(self.mincelly, cy)
                self.maxcellx = max(self.maxcellx, cx + lx - 1)
                self.maxcelly = max(self.maxcelly, cy + ly - 1)
        print(self.mincellx, self.maxcellx, self.mincelly, self.maxcelly)
        #for instr in self.instruments:
        #    instr.draw()

        self.fen.mainloop()

        print("Fin de la fonction run de dashboard")
        self.queue.put("STOP")

    def putData(self, data):
        #print (f"Dashboard : Réception de {data.type}")
        for ins in self.instruments:
            ins.putData(data)
        return

    def function(self, v):
        return (v + 1)


