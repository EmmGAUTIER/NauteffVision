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

import math
import tkinter
from functools import partial
import time

from numpy.distutils.fcompiler import none

import calculs
import data as data


def arrow_coords_create1(origin, angle, l1, style):
    """

    """
    x0 = origin[0]
    y0 = origin[1]
    cosinus = math.cos(angle)
    sinus = math.sin(angle)
    pts = None

    if style == "pin":
        dx = l1 * sinus * 0.02
        dy = -l1 * cosinus * 0.02
        pts = [
            x0 - 2 * dx,
            y0 + 2 * dy,
            x0 + l1 * cosinus,
            y0 - l1 * sinus,
            x0 + 2 * dx,
            y0 - 2 * dy,
        ]
        return pts


def arrow_coords_create(origin, angle, l1, l2, head, larg):
    x0 = origin[0]
    y0 = origin[1]
    cos = math.cos(angle)
    sin = math.sin(angle)
    dx = larg * sin
    dy = -larg * cos
    d2x = head * sin
    d2y = -head * cos

    pts = [x0 - l2 * cos + dx,  # pt 1
           y0 + l2 * sin - dy,

           x0 + (l1 - head) * cos + dx,  # pt 2
           y0 - (l1 - head) * sin - dy,

           x0 + (l1 - head) * cos + d2x,  # pt 3
           y0 - (l1 - head) * sin - d2y,

           x0 + l1 * cos + 0,  # pt 4
           y0 - l1 * sin - 0,

           # x0 - (l1 - head) * cos - d2x,  # pt 5
           # y0 - (l1 - head) * sin - d2y,
           x0 + (l1 - head) * cos - d2x,  # pt 3
           y0 - (l1 - head) * sin + d2y,

           x0 + (l1 - head) * cos - dx,  # pt 6
           y0 - (l1 - head) * sin + dy,

           x0 - l2 * cos - dx,  # pt 7
           y0 + l2 * sin + dy
           ]

    return pts


class Gauje():

    def __init__(self, canvas, cx, cy, size, start_a, end_a, start_v, end_v,
                 grads=[], colors=[]):
        self.canvas = canvas
        self.cx = cx
        self.cy = cy
        self.size = size
        self.hands = []
        self.start_a = start_a
        self.end_a = end_a
        self.start_v = start_v
        self.end_v = end_v
        self.grads = grads
        self.colors = colors
        self.ghand = None
        self.value = None
        return

    def draw(self):
        self.canvas.create_arc(self.cx - self.size, self.cy - self.size, self.cx + self.size, self.cy + self.size,
                               start=self.start_a - 90, extent=self.end_a - self.start_a
                               )
        self.canvas.create_arc(self.cx - self.size * 0.8, self.cy - self.size * 0.8, self.cx + self.size * 0.8,
                               self.cy + self.size * 0.8,
                               start=self.start_a - 90, extent=self.end_a - self.start_a
                               )
        return

    def putData(self, value):
        if self.ghand is not None:
            self.canvas.delete(self.ghand)
        if self.value is not None:
            # angle
            # deg2rad(angle)
            return


class Instrument(data.DataListener, data.DataEmitter):

    def __init__(self, parent, config):
        self.parent = parent
        self.icanvas = None
        self.cellx = int(config["cell_origx"])
        self.celly = int(config["cell_origy"])
        self.sizex = None
        self.sizey = None
        self.colors = None
        self.font_small_normal = None
        self.font_medium_normal = None
        self.font_large_normal = None
        if "cell_width" in config:
            self.cellsizex = int(config["cell_width"])
        else:
            self.cellsizex = 1
        if "cell_height" in config:
            self.cellsizey = int(config["cell_height"])
        else:
            self.cellsizey = 1

    def set_colors(self, clrs):
        self.colors = clrs

    def setcanvas(self, cvs):
        self.icanvas = cvs

    def draw(self):
        if self.icanvas == None:
            return
        self.sizex = self.icanvas.winfo_width()
        self.sizey = self.icanvas.winfo_height()
        self.middlex = self.sizex / 2
        self.middley = self.sizey / 2
        self.radius_gauje = min(self.sizex, self.sizey) * 0.9 * 0.5

        # print('- - - > ', self.sizex, self.sizey)
        self.icanvas.delete("all")
        # self.icanvas.create_line(0, 0, 10, 10)
        self.icanvas.create_rectangle(1, 1, self.sizex - 2, self.sizey - 2)

    @staticmethod
    def create_instrument(parent, config):
        instrument = None
        if config["type"] == "compass":
            instrument = Instrument_compass(parent, config)
        elif config["type"] == "wind":
            instrument = Instrument_Wind(parent, config)
        elif config["type"] == "APcontrol":
            instrument = Instrument_APcontrol(parent, config)
        elif config["type"] == "clock":
            instrument = Instrument_clock(parent, config)
        elif config["type"] == "speed":
            instrument = Instrument_speed(parent, config)
        elif config["type"] == "tide":
            instrument = Instrument_Tide(parent, config)
        elif config["type"] == "attitude":
            print("Création d'un afficheur d'assiette")
            instrument = Instrument_Attitude(parent, config)
        else:
            instrument = Instrument(parent, config)
        # instrument = Instrument_compass(config)
        return instrument


class Instrument_Attitude(Instrument):

    def __init__(self, parent, config):
        print("Je crée l'afficheur d'assiette")
        super().__init__(parent, config)
        self.dtypes = [data.dataAttitude]
        self.heading = None
        self.pitch = None
        self.roll = None
        self.origin = config.get("origin")
        self.title = config.get("title")
        self.r1 = 2  # rayon des cercles autour
        self.r2 = 1  # autre rayon
        self.angle_rect = 45. * math.pi / 180.
        self.attdrawing = []
        self.symbol_boat = None
        #print("--> Création cadran attitude")
        return

    def putData(self, data):
        # print(f"Instrument_Attitude reçoit : {data.type}")

        if type(data) in self.dtypes:
            # print (f"Instrument_Attitude reçoit une donnée de : {data.origin}")
            if self.origin is None or data.origin == self.origin:
                #print(f"-->  Instrument_Attitude affiche : {data.heading}, {data.pitch} {data.roll}")
                self.heading = data.heading
                self.pitch = data.pitch
                self.roll = data.roll
                self.refreshData()
        return

    def draw(self):
        super().draw()
        self.r1 = int(self.radius_gauje * 0.7)
        self.r2 = int(self.radius_gauje)
        self.extcircle = self.icanvas.create_oval((self.middlex - self.r1, self.middley - self.r1),
                                                  (self.middlex + self.r1, self.middley + self.r1), width=2,
                                                  outline=self.colors["fore"])
        self.intcircle = self.icanvas.create_oval((self.middlex - self.r2, self.middley - self.r2),
                                                  (self.middlex + self.r2, self.middley + self.r2), width=2,
                                                  outline=self.colors["fore"])
        self.grads = []
        for angledeg in range(-60, 70, 10):
            anglerad = calculs.deg2rad(angledeg)
            cos_a = math.cos(anglerad)
            sin_a = math.sin(anglerad)
            grad = self.icanvas.create_line(self.middlex + self.r1*cos_a,
                                            self.middley - self.r1*sin_a,
                                            self.middlex + self.r2*cos_a,
                                            self.middley - self.r2*sin_a,
                                            width=2)
            self.grads.append(grad)
            # dessin de la barre qui symbolise le navire
            self.symbol_boat = self.icanvas.create_line(self.middlex - self.r2 *0.30, self.middley,
                                                        self.middlex + self.r2 *0.30, self.middley,
                                                        fill="orange",
                                                        width=3)

    def refreshData(self):

        #print (f"--> {self.pitch}  {self.roll}")
        if self.pitch is not None and self.roll is not None:
            cos_a = math.cos(self.angle_rect + self.roll)
            sin_a = math.sin(self.angle_rect + self.roll)

            for cadre in self.attdrawing:
                self.icanvas.delete(cadre)

            tl = (self.middlex + math.cos(math.pi-self.angle_rect + self.roll) * self.r1,
                  self.middley - math.sin(math.pi-self.angle_rect + self.roll) * self.r1)

            tr = (self.middlex + math.cos(+self.angle_rect + self.roll) * self.r1,
                  self.middley - math.sin(+self.angle_rect + self.roll) * self.r1)

            br = (self.middlex + math.cos(-self.angle_rect + self.roll) * self.r1,
                  self.middley - math.sin(-self.angle_rect + self.roll) * self.r1)

            bl = (self.middlex + math.cos(math.pi+self.angle_rect + self.roll) * self.r1,
                  self.middley - math.sin(math.pi+self.angle_rect + self.roll) * self.r1)

            hl = (bl[0] + (tl[0]-bl[0]) * (1.0 + math.sin(self.pitch)) * 0.5,
                  bl[1] + (tl[1]-bl[1]) * (1.0 + math.sin(self.pitch)) * 0.5)
            hr = (br[0] + (tr[0]-br[0]) * (1.0 + math.sin(self.pitch)) * 0.5,
                  br[1] + (tr[1]-br[1]) * (1.0 + math.sin(self.pitch)) * 0.5)

            cadre_sky = self.icanvas.create_polygon([tl, tr, hr, hl],
                                          width=2,
                                          fill = "lightblue",
                                          outline=self.colors["fore"])
            self.attdrawing.append(cadre_sky)

            cadre_sea = self.icanvas.create_polygon([hl, hr, br, bl],
                                          width=2,
                                          fill = "darkblue",
                                          outline=self.colors["fore"])
            self.attdrawing.append(cadre_sea)
            grad_roll = self.icanvas.create_line(self.middlex - math.sin(self.roll) * self.r1*0.8,
                                                 self.middley - math.cos(self.roll) * self.r1*0.8,
                                                 self.middlex - math.sin(self.roll) * self.r1,
                                                 self.middley - math.cos(self.roll) * self.r1)
            self.attdrawing.append(grad_roll)
            self.icanvas.tag_raise(self.symbol_boat)
        """
        centredrw_x = self.middlex
        centredrw_y = self.middley + math.sin(self.pitch) * self.radius_gauje
        cos = math.cos(self.roll)
        sin = math.sin(self.roll)
        dx = self.r1 * sin * 0.2
        dy = self.r1 * cos * 0.1
        pts = [
            centredrw_x + self.r2 * cos - dx * sin,
            centredrw_y + self.r2 * sin + dy * cos,

            centredrw_x + self.r2 * cos + dx * sin,
            centredrw_y + self.r2 * sin - dy * sin,

            centredrw_x - self.r2 * cos + dx * sin,
            centredrw_y - self.r2 * sin - dy * cos,

            centredrw_x - self.r2 * cos - dx * sin,
            centredrw_y - self.r2 * sin + dy * sin,
        ]
        if self.attdrawing is not None:
            self.icanvas.delete(self.attdrawing)
        self.attdrawing = self.icanvas.create_polygon(pts)
        """
        return


class Instrument_clock(Instrument):

    def __init__(self, parent, config):
        super().__init__(parent, config)
        print("Création d'un afficheur d'horloge")
        self.hour = None
        self.min = None
        self.min = None
        self.arrow_hour = None
        self.arrow_min = None
        self.arrow_sec = None
        self.text = None

    def draw(self):
        super().draw()
        r1 = int(self.radius_gauje)
        r2 = int(self.radius_gauje * 0.7)
        self.extcircle = self.icanvas.create_oval((self.middlex - r1, self.middley - r1),
                                                  (self.middlex + r1, self.middley + r1), width=2,
                                                  outline=self.colors["fore"])
        self.intcircle = self.icanvas.create_oval((self.middlex - r2, self.middley - r2),
                                                  (self.middlex + r2, self.middley + r2), width=2,
                                                  outline=self.colors["fore"])
        for i in range(12):
            angle = calculs.deg2rad((i + 1) * 30)

            self.icanvas.create_text(self.middlex + ((r1 + r2) / 2) * math.cos(angle),
                                     self.middley - ((r1 + r2) / 2) * math.sin(angle),
                                     text=str(i + 1),
                                     anchor="center",
                                     font=self.parent.font_medium_normal,
                                     fill=self.colors["fore"])

        self.text = self.icanvas.create_text(self.middlex, self.sizey * 0.9, text="?",
                                             anchor="center", font=self.parent.font_large_normal,
                                             fill=self.colors["fore"])

    def get_data_list_in(self):
        return ["Time", "SysTime"]

    def putData(self, data):
        if data.type == "SysTime":
            self.icanvas.itemconfig(self.text,
                                    text=str(data.values.get("Hour")) + " : " +
                                         str(data.values.get("Minute")) + " : " +
                                         str(data.values.get("Second")))
            self.icanvas.delete(self.arrow_hour)
            self.icanvas.delete(self.arrow_min)
            self.icanvas.delete(self.arrow_sec)

            # print  (data.values.get("Hour"), " : ", data.values.get("Minute"), " : ",data.values.get("Second"))
            angle = calculs.deg2rad(data.values.get("Hour") * 30 + data.values.get("Minute") * 0.5)
            larg = self.radius_gauje / 15
            dx = larg * math.sin(angle)
            dy = -larg * math.cos(angle)
            pts = [self.middlex + ((self.radius_gauje * 0.2) * math.cos(angle) + dx),
                   self.middley - ((self.radius_gauje * 0.2) * math.sin(angle) + dy),
                   self.middlex + ((self.radius_gauje * 0.2) * math.cos(angle) - dx),
                   self.middley - ((self.radius_gauje * 0.2) * math.sin(angle) - dy),
                   self.middlex + ((self.radius_gauje * 0.7) * math.cos(angle) - dx),
                   self.middley - ((self.radius_gauje * 0.7) * math.sin(angle) - dy),
                   self.middlex + ((self.radius_gauje * 0.7) * math.cos(angle) - 2 * dx),
                   self.middley - ((self.radius_gauje * 0.7) * math.sin(angle) - 2 * dy),
                   self.middlex + ((self.radius_gauje * 1.0) * math.cos(angle)),
                   self.middley - ((self.radius_gauje * 1.0) * math.sin(angle)),
                   self.middlex + ((self.radius_gauje * 0.7) * math.cos(angle) + 2 * dx),
                   self.middley - ((self.radius_gauje * 0.7) * math.sin(angle) + 2 * dy),
                   self.middlex + ((self.radius_gauje * 0.7) * math.cos(angle) + dx),
                   self.middley - ((self.radius_gauje * 0.7) * math.sin(angle) + dy)
                   ]

            self.arrow_hour = self.icanvas.create_polygon(pts, width=3,
                                                          outline=self.colors["fore"],
                                                          fill='')

            # Minute arrow
            pts = arrow_coords_create((self.middlex, self.middley),
                                      calculs.deg2rad(data.values.get("Minute") * 6),
                                      self.radius_gauje * 0.9,
                                      self.radius_gauje * 0.1,
                                      self.radius_gauje * 0.03,
                                      self.radius_gauje * 0.01)
            self.arrow_min = self.icanvas.create_polygon(pts, width=2,
                                                         outline=self.colors["fore"],
                                                         fill='')

            pts = arrow_coords_create1((self.middlex, self.middley),
                                       calculs.deg2rad(data.values.get("Second") * 6),
                                       self.radius_gauje * 0.9, "pin")
            # print("Points minute : ", pts)
            self.arrow_sec = self.icanvas.create_polygon(pts, width=1,
                                                         outline=self.colors["fore"],
                                                         fill='')

        # pts = arrow_coords_create((0, 0), 0, 0, self.radius_gauje * 0.7, 1, 1)
        # self.arrow_sec = self.icanvas.create_polygon(pts, width=3,
        #                                             outline=self.colors["fore"],
        #                                             fill='')

        return


class Instrument_speed(Instrument):

    def __init__(self, parent, config):
        super().__init__(parent, config)
        self.radius_gauje = None
        self.value = None
        self.gauje = None
        if "title" in config:
            self.title = config["title"]
        else:
            self.title = None
        self.max = config["max"]
        return

    def draw(self):
        super().draw()
        self.gauje = Gauje(self.icanvas,
                           self.sizex / 2,
                           self.sizey / 2,
                           min(self.sizex, self.sizey),
                           -150, 150, 0, self.max,
                      None, None)

        return


class Instrument_compass(Instrument):

    def __init__(self, parent, config):
        super().__init__(parent, config)
        self.heading = None
        self.dtypes = [data.dataAttitude]
        self.origin = config.get("origin")
        self.title = config.get("title")
        self.lblsdir = ["N", "30", "60", "E", "120", "150", "S", "210", "240", "W", "300", "330"]
        self.extcircle = None
        self.intcircle = None
        self.arrow = None
        self.text = None

    def get_data_list_in(self):
        return ["HDG/M", "HDG/T", "ATTITUDE"]

    def draw(self):
        super().draw()
        # print ("Instrument_compass -> draw()")

        r1 = int(self.radius_gauje)
        r2 = int(self.radius_gauje * 0.7)
        self.extcircle = self.icanvas.create_oval((self.middlex - r1, self.middley - r1),
                                                  (self.middlex + r1, self.middley + r1), width=2,
                                                  outline=self.colors["fore"])
        self.intcircle = self.icanvas.create_oval((self.middlex - r2, self.middley - r2),
                                                  (self.middlex + r2, self.middley + r2), width=2,
                                                  outline=self.colors["fore"])
        for i in range(0, 360, 10):
            angle = calculs.deg2rad(i)
            if i % 3 != 0:
                self.icanvas.create_line((self.middlex + r1 * math.cos(angle),
                                          self.middley - r1 * math.sin(angle)),
                                         (self.middlex + r2 * math.cos(angle),
                                          self.middley - r2 * math.sin(angle)),
                                         width=1, fill=self.colors["fore"])
            else:
                self.icanvas.create_text(self.middlex + ((r1 + r2) / 2) * math.cos(angle),
                                         self.middley - ((r1 + r2) / 2) * math.sin(angle),
                                         text=self.lblsdir[int(i / 30)],
                                         anchor="center",
                                         font=self.parent.font_medium_normal,
                                         fill=self.colors["fore"])

        self.text = self.icanvas.create_text(self.middlex, self.middley, text="?",
                                             anchor="center", font=self.parent.font_large_normal,
                                             fill=self.colors["fore"])

    def putData(self, data):
        angle = None
        # print(f"Instrument_Compass reçoit : {data.type}")

        if type(data) in self.dtypes:
            # print (f"Instrument_Compass reçoit une donnée de : {data.origin}")
            if self.origin is None or data.origin == self.origin:
                #print(f"-->  Instrument_Compass affiche : {data.heading}, {data.pitch} {data.roll}")
                self.heading = data.heading
                angle = self.heading
                hdgdeg = calculs.rad2deg(angle)
                # self.pitch = data.pitch # useless
                # self.roll = data.roll   #useless
                # self.refreshData()

        # if data.type == "HDG/M" and data.values.get("Heading/Mag") is not None:
        #    hdg = data.values.get("Heading/Mag")
        #    angle = deg2rad(hdg)

        # if type(data == "ATTITUDE") and data.heading is not None:
        #    hdg = data.values.get("Heading/Mag")
        #    angle = deg2rad(hdg)

        if angle is not None and self.extcircle is not None:
            #print("Ça dessine le cap ! ", str(hdgdeg))
            str_hdg_deg = f"{int(hdgdeg)}"
            self.icanvas.itemconfig(self.text, text=str_hdg_deg)
            # print(type(self.text))
            self.icanvas.delete(self.arrow)
            larg = self.radius_gauje / 15
            dx = larg * math.sin(angle)
            dy = -larg * math.cos(angle)
            pts = [self.middlex + (self.radius_gauje * 0.2) * math.cos(angle) + dx,
                   self.middley - (self.radius_gauje * 0.2) * math.sin(angle) - dy,
                   self.middlex + (self.radius_gauje * 0.2) * math.cos(angle) - dx,
                   self.middley - (self.radius_gauje * 0.2) * math.sin(angle) + dy,
                   self.middlex + (self.radius_gauje * 0.7) * math.cos(angle) - dx,
                   self.middley - (self.radius_gauje * 0.7) * math.sin(angle) + dy,
                   self.middlex + (self.radius_gauje * 0.7) * math.cos(angle) - 2 * dx,
                   self.middley - (self.radius_gauje * 0.7) * math.sin(angle) + 2 * dy,
                   self.middlex + (self.radius_gauje * 1.0) * math.cos(angle),
                   self.middley - (self.radius_gauje * 1.0) * math.sin(angle),
                   self.middlex + (self.radius_gauje * 0.7) * math.cos(angle) + 2 * dx,
                   self.middley - (self.radius_gauje * 0.7) * math.sin(angle) - 2 * dy,
                   self.middlex + (self.radius_gauje * 0.7) * math.cos(angle) + dx,
                   self.middley - (self.radius_gauje * 0.7) * math.sin(angle) - dy
                   ]
            self.arrow = self.icanvas.create_polygon(pts, width=3, outline=self.colors["fore"], fill='')

        return


class Instrument_Tide(Instrument):

    def __init__(self, parent, config):
        super(Instrument_Tide, self).__init__(parent, config)
        self.h1 = None
        self.h2 = None
        self.t1 = None
        self.t2 = None
        self.entryh1 = None
        self.entryh2 = None
        self.entryt1 = None
        self.entryt2 = None
        self.btnCompute = None
        self.panneau = None

    def get_data_list_in(self):
        return ["SYSCLOCK"]

    def draw(self):
        super().draw()
        # print ("Instrument Tide draw")
        # self.sizex
        pts = [
            self.sizex * 0.1, self.sizey * 0.3,
            self.sizex * 0.1, self.sizey * 0.9,
            self.sizex * 0.9, self.sizey * 0.9,
            self.sizex * 0.9, self.sizey * 0.3
        ]
        # self.panneau =

        # self.icanvas.create_line(pts)
        # self.entryh1 = tkinter.Entry(self.icanvas)

        # self.entryh1.bind('<Configure>', self.rien)
        # self.entryh1.place(x=10, y=10, width = 60, height = 28)

        # self.entryh1 = tkinter.Entry(self.icanvas, text="Heure 1", font=self.parent.font_large_normal)

        # mystr = tkinter.StringVar()
        # mystr.set('matin')

        # self.entryh1 = tkinter.Entry(self.icanvas) #, textvariable=mystr)
        # self.btnCompute = tkinter.Button(self.icanvas,  text="Calcul",
        #                                  font=self.parent.font_large_normal,
        #                                  command=partial(self.fctCommand, "Calcul"))
        # self.btnCompute.place(x=30, y=30)

        # self.entryh1.place(x=30, y=30)
        # self.icanvas.create_
        sx = int(self.sizex * 0.2)
        sy = int(self.sizey * 0.2)
        # self.entryh1().place( x = 20, y=20)
        # self.entryh1.place(x=int(self.sizex * 0.1), y=int(self.sizey * 0.1), width=sx, height=sy)
        # self.entryh1.place(x=20, y=20, width=sx, height=sy)
        pass

    def fctCommand(self, data):
        pass

    def rien(self):
        pass

    def put_data(self, data):
        pass


class Instrument_Wind(Instrument):

    def __init__(self, parent, config):
        super().__init__(parent, config)
        self.lblsdir = ["0", "30", "60", "90", "120", "150", "180", "150", "120", "90", "60", "30"]
        self.aiguille = none

    def get_data_list_in(self):
        # return ["Wind/App", "Wind/True", "SpeedOW"]
        return ["MWV"]

    def draw(self):
        super().draw()
        # print ("Instrument Wind draw")

        r1 = int(self.radius_gauje)
        r2 = int(self.radius_gauje * 0.7)

        self.icanvas.create_arc(self.middlex - (r1 + r2) / 2, self.middley - (r1 + r2) / 2,
                                self.middlex + (r1 + r2) / 2, self.middley + (r1 + r2) / 2,
                                start=90, extent=120, style="arc", outline="red", width=r1 - r2)

        self.icanvas.create_arc(self.middlex - (r1 + r2) / 2, self.middley - (r1 + r2) / 2,
                                self.middlex + (r1 + r2) / 2, self.middley + (r1 + r2) / 2,
                                start=330, extent=120, style="arc", outline="green", width=r1 - r2)

        self.icanvas.create_arc(self.middlex - (r1 + r2) / 2, self.middley - (r1 + r2) / 2,
                                self.middlex + (r1 + r2) / 2, self.middley + (r1 + r2) / 2,
                                start=210, extent=120, style="arc", outline="white", width=r1 - r2)

        self.icanvas.create_oval((self.middlex - r1, self.middley - r1),
                                 (self.middlex + r1, self.middley + r1), width=2,
                                 outline=self.colors["fore"])
        self.icanvas.create_oval((self.middlex - r2, self.middley - r2),
                                 (self.middlex + r2, self.middley + r2), width=2,
                                 outline=self.colors["fore"])

        for i in range(0, 360, 10):
            angle = calculs.deg2rad(i)
            if i % 3 != 0:
                self.icanvas.create_line((self.middlex + r1 * math.cos(angle),
                                          self.middley - r1 * math.sin(angle)),
                                         (self.middlex + r2 * math.cos(angle),
                                          self.middley - r2 * math.sin(angle)),
                                         width=1, fill=self.colors["fore"])
            else:
                self.icanvas.create_text(self.middlex + ((r1 + r2) / 2) * math.cos(angle),
                                         self.middley - ((r1 + r2) / 2) * math.sin(angle),
                                         text=self.lblsdir[int(i / 30)],
                                         anchor="center",
                                         font=self.parent.font_medium_normal,
                                         fill=self.colors["fore"])

    def put_data(self, data):
        if data.type == "MWV":
            r1 = int(self.radius_gauje)
            dire = data.values.get("WindAngle/App")
            if self.aiguille is not None:
                self.icanvas.delete(self.aiguille)
            self.aiguille = self.icanvas.create_line(self.middlex, self.middley,
                                                     self.middlex + r1 * math.cos(dire),
                                                     self.middley + r1 * math.sin(dire))
        pass


def fctReflexe():
    print("========>> fctReflexe()")


class Instrument_APcontrol(Instrument):

    def __init__(self, parent, config):
        super().__init__(parent, config)
        self.btnAuto = None
        self.btnStandBy = None
        self.btnPlus1 = None
        self.btnPlus10 = None
        self.btnMinus1 = None
        self.btnMinus10 = None

    def draw(self):
        super().draw()
        if self.btnAuto is None:
            self.btnAuto = tkinter.Button(self.icanvas, text="Auto",
                                          font=self.parent.font_large_normal,
                                          command=partial(self.fctCommand, "-Auto"))
            self.btnStandBy = tkinter.Button(self.icanvas, text="Stand by",
                                             font=self.parent.font_large_normal,
                                             command=partial(self.fctCommand, "Stand by"))
            self.btnPlus1 = tkinter.Button(self.icanvas, text="+1",
                                           font=self.parent.font_large_normal,
                                           bg="green",
                                           command=partial(self.fctCommand, "+1"))
            self.btnPlus10 = tkinter.Button(self.icanvas, text="+10",
                                            font=self.parent.font_large_normal,
                                            bg="green",
                                            command=partial(self.fctCommand, "+10"))
            self.btnMinus1 = tkinter.Button(self.icanvas, text="-1",
                                            font=self.parent.font_large_normal,
                                            bg="red",
                                            command=partial(self.fctCommand, "-1"))
            self.btnMinus10 = tkinter.Button(self.icanvas, text="-10",
                                             font=self.parent.font_large_normal,
                                             bg="red",
                                             fg="white",
                                             highlightcolor="blue",
                                             command=partial(self.fctCommand, "-10"))

        self.btnAuto.configure(font=self.parent.font_medium_normal)
        self.btnStandBy.configure(font=self.parent.font_medium_normal)
        self.btnPlus1.configure(font=self.parent.font_medium_normal)
        self.btnPlus10.configure(font=self.parent.font_medium_normal)
        self.btnMinus1.configure(font=self.parent.font_medium_normal)
        self.btnMinus10.configure(font=self.parent.font_medium_normal)

        # self.btnPlus1.configure(width=2)
        sx = int(self.sizex * 0.2)
        sy = int(self.sizey * 0.2)
        self.btnAuto.place(x=int(self.sizex * 0.1), y=int(self.sizey * 0.1), width=sx, height=sy)
        self.btnStandBy.place(x=int(self.sizex * 0.4), y=int(self.sizey * 0.1), width=sx, height=sy)
        self.btnPlus1.place(x=int(self.sizex * 0.4), y=int(self.sizey * 0.4), width=sx, height=sy)
        self.btnPlus10.place(x=int(self.sizex * 0.4), y=int(self.sizey * 0.7), width=sx, height=sy)
        self.btnMinus1.place(x=int(self.sizex * 0.1), y=int(self.sizey * 0.4), width=sx, height=sy)
        self.btnMinus10.place(x=int(self.sizex * 0.1), y=int(self.sizey * 0.7), width=sx, height=sy)

    def fctCommand(self, cmd):
        print("commande : ", cmd)
        self.parent.queue .put(data.dataAPCommand(time.time(), "Dashboard", cmd))
