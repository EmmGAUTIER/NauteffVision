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

import gi
# import os
import sys

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango, GLib
import cairo

import time
import datetime
from abc import ABC
# from functools import partial

import pytz

import data
import calculs
import math


def gen_ticks(min_val, max_val):
    """
    genticks(min_val, max_val)
    min_val : valeur de début
    return : liste des graduations

    Cette fonction retourne une liste de graduations entre 0 et max_val.
    min_val n'est pas encore pris en compte.
    La liste comporte des tuples à deux éléments. Le premier élément contient
    la valeur, le deuxième élément contient une chaîne avec la valeur à afficher.
    Nouvelle ligne de doc.
    """

    diff = max_val - min_val
    log10diff = math.log10(diff)
    rnd = math.trunc(log10diff)
    mant = math.pow(10., log10diff - rnd)
    # tick = mant * fact
    tick = mant
    if tick < 2:
        tick = 1
    elif tick < 4:
        tick = 2
    else:
        tick = 5
    tick = math.pow(10., rnd - 1) * tick * 2

    tick_list = []
    for ival in range(0, (math.trunc(max_val / tick)) + 1):
        tick_list.append((0 + ival * tick, f"{ival * tick:.0f}"))

    return tick_list


class ColoredArc:
    def __init__(self, start_angle, end_angle, color):
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.color = color
        return

    def draw(self, cr, center_x, center_y, radius, fore_color):
        return


class ArcGradue:
    ARC = 1
    CIRCLE = 2

    # def __init__(self, start_angle, end_angle, min_value, max_value):
    def __init__(self, grad_type=ARC, start_angle=None, end_angle=None, min_value=None, max_value=None):
        self.grad_type = type
        # Min and max displayed values, They may be outside the circle
        self.min_disp_value = min_value
        self.max_disp_value = max_value
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.min_value = min_value
        self.max_value = max_value

        #    self.start_angle = start_angle if start_angle is not None else 0
        #    self.end_angle = end_angle if end_angle is not None else 360
        #    self.min_value = min_value
        #    self.max_value = max_value

        self.ticks = []
        self.sub_ticks = []
        # self.set_ticks(gen_ticks(min_value, max_value))
        self.zones = []

    def add_zone(self, start_value: float, end_value: float, color: object) -> None:
        self.zones.append((start_value, end_value, color))
        return

    def set_ticks(self, ticks):
        self.ticks = ticks
        # Graduations secondaires
        self.sub_ticks = []
        nb_sub_ticks = (len(self.ticks) - 1) * 10
        amplitude = ticks[-1][0] - ticks[0][0]
        for itick in range(nb_sub_ticks):
            self.sub_ticks.append(ticks[0][0] + amplitude * itick / nb_sub_ticks)
        return

    def set_sub_ticks(self, ticks):
        self.sub_ticks = ticks

    def get_angle(self, value):
        if self.grad_type == ArcGradue.ARC:
            if self.min_value <= value <= self.max_value:
                if self.end_angle < self.start_angle:
                    sag, eag = self.start_angle, self.end_angle
                else:
                    sag, eag = self.start_angle, self.end_angle - math.pi * 2
                angle = sag + (eag - sag) * (value - self.min_value) / (self.max_value - self.min_value)
            else:
                angle = None
            return angle
        else:
            angle = - 2. * math.pi * (value - self.min_value) / (self.max_value - self.min_value)
            return angle

    def draw(self, cr, center_x, center_y, radius, fore_color):
        # print("---> ArcGradué :: draw()")

        # Selection de la police de caractères et de la couleur
        # cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(radius * 0.15)
        cr.set_source_rgb(*fore_color)

        if self.grad_type == ArcGradue.ARC:
            # Dessin des graduations principales
            if self.end_angle < self.start_angle:
                sag, eag = self.start_angle, self.end_angle
            else:
                sag, eag = self.start_angle, self.end_angle - math.pi * 2
        else:
            sag, eag = math.pi / 2., -3. * (math.pi / 2)

        # print(f"   {180. * eag / math.pi:5.0f} {180. * sag / math.pi:5.0f}")

        # Draw zones
        for zone in self.zones:
            # print(f"----> zone     {zone}")
            # print(f"----> zone[0]  {zone[0]}")
            a1 = -1.0 * self.get_angle(zone[0])
            a2 = -1.0 * self.get_angle(zone[1])
            # print(f" === ({a1},{a2})")
            cr.set_source_rgb(*zone[2])
            cr.set_line_width(radius * 0.1)
            cr.move_to(center_x + math.cos(a1) * radius * 0.95,
                       center_y + math.sin(a1) * radius * 0.95)
            cr.arc(center_x, center_y, radius * .95, a1, a2)
            cr.stroke()
            pass

        if self.grad_type == ArcGradue.ARC:
            # Dessin de l'arc de cercle
            # Rappel : les coordonnées y sont croissantes vers le bas
            cr.set_source_rgb(*fore_color)
            cr.set_line_width(radius * 0.02)
            cr.set_line_cap(cairo.LINE_CAP_ROUND)
            sa, ea = - self.start_angle, - self.end_angle
            cr.move_to(center_x + math.cos(sa) * radius,
                       center_y + math.sin(sa) * radius)
            cr.arc(center_x, center_y, radius, sa, ea)
            cr.stroke()

            for tick in self.ticks:
                angle = sag + (eag - sag) * (tick[0] - self.min_value) / (self.max_value - self.min_value)
                # print (f"==> {180. * angle /math.pi}")

                inner_x = center_x + (radius * 0.8) * math.cos(angle)
                inner_y = center_y - (radius * 0.8) * math.sin(angle)
                outer_x = center_x + radius * math.cos(angle)
                outer_y = center_y - radius * math.sin(angle)

                cr.move_to(inner_x, inner_y)
                cr.line_to(outer_x, outer_y)
                cr.stroke()

                # Écriture de la valeur
                text = tick[1]
                extents = cr.text_extents(text)
                diagonale = math.sqrt(extents.width * extents.width + extents.height * extents.height)
                cr.move_to(center_x + (radius * 0.8 - diagonale * 0.6) * math.cos(angle) - extents.width / 2,
                           center_y - (radius * 0.8 - diagonale * 0.6) * math.sin(angle) + extents.height / 2.)
                cr.show_text(text)

        else:
            # Dessin du cercle extérieur
            cr.set_source_rgb(*fore_color)
            cr.set_line_width(radius * 0.02)
            cr.move_to(center_x + radius, center_y)
            cr.arc(center_x, center_y, radius, 0, 2 * math.pi)
            cr.stroke()
            # print (self.ticks)
            #
            for angle, label in self.ticks:
                # angle = calculs.deg2rad(angle)
                angle = self.get_angle(angle)
                cr.move_to(center_x + 0.8 * radius * math.cos(angle), center_y + 0.8 * radius * math.sin(angle))
                cr.line_to(center_x + radius * math.cos(angle), center_y + radius * math.sin(angle))
                cr.stroke()
                # Dessin de la graduation
                extents = cr.text_extents(label)
                diagonale = math.sqrt(extents.width * extents.width + extents.height * extents.height)
                cr.move_to(center_x + (radius * 0.8 - diagonale * 0.6) * math.cos(angle) - extents.width / 2,
                           center_y - (radius * 0.8 - diagonale * 0.6) * math.sin(angle) + extents.height / 2.)
                cr.show_text(label)
            pass
        # if self.type == CIRCLE

    def draw_zone(self, cr, center_x, center_y, radius, zone):
        # print(f" --> draw_zone :   {center_x}, {center_y}  radius = {radius} ")

        start_value, end_value, color = zone

        start_angle = self.start_angle + (start_value - self.min_value) / (self.max_value - self.min_value) * (
                self.end_angle - self.start_angle)
        end_angle = self.start_angle + (end_value - self.min_value) / (self.max_value - self.min_value) * (
                self.end_angle - self.start_angle)

        cr.set_source_rgb(*color)
        cr.move_to(center_x + (radius * 0.95) * math.cos(math.radians(start_angle)),
                   center_y + (radius * 0.95) * math.sin(math.radians(start_angle)))
        cr.set_line_width(radius * .1)
        # cr.arc(center_x, center_y, radius - 10, math.radians(start_angle), math.radians(end_angle))
        cr.arc(center_x, center_y, radius * 0.95, start_angle, end_angle)
        cr.stroke()
        cr.close_path()
        cr.fill()


class Aiguille:
    def __init__(self, style):
        self.style = style
        self.L1, self.L2, self.L3 = None, None, None
        self.W1 = self.W2 = None, None
        self.plain = True
        self.angle = None

        if self.style == "HDG":
            self.L1 = 0.90
            self.L2 = 0.50
            self.L3 = 0.80
            self.W1 = 0.10
            self.W2 = 0.15
            self.plain = False
        if self.style == "STD":
            self.L1 = 0.95
            self.L2 = 0.50
            self.L3 = 0.80
            self.W1 = 0.15
            self.W2 = None
            self.plain = True
        if self.style == "THICK":
            self.L1 = 0.95
            self.L2 = 0.50
            self.L3 = 0.80
            self.W1 = 0.15
            self.W2 = None
            self.plain = True
        if self.style == "THIN":
            self.L1 = 0.95
            self.L2 = 0.05
            self.L3 = 0.90
            self.W1 = 0.05
            self.W2 = 0.05
            self.plain = True

    def set_angle(self, angle):
        self.angle = angle

    def draw(self, cr, center_x, center_y, length, color):

        if self.angle is None:
            return

        cos_a, sin_a = math.cos(self.angle), -math.sin(self.angle)

        # Pour mise au point : dessin d'un trait d'axe
        # cr.move_to(center_x - (length * 0.8) * cos_a, center_y - (length * 0.8) * sin_a)
        # cr.line_to(center_x + (length * 1.2) * cos_a, center_y + (length * 1.2) * sin_a)
        # cr.stroke()

        cr.set_source_rgb(*color)
        cr.set_line_width(length * 0.03)
        ptq = (center_x - cos_a * length * self.L2,
               center_y - sin_a * length * self.L2)

        ptm = (center_x + cos_a * length * self.L2,
               center_y + sin_a * length * self.L2)

        pte = (center_x + cos_a * length * self.L1,
               center_y + sin_a * length * self.L1)

        cr.move_to(ptq[0] - sin_a * length * self.W1, ptq[1] + cos_a * length * self.W1)
        cr.line_to(ptq[0] + sin_a * length * self.W1, ptq[1] - cos_a * length * self.W1)
        cr.line_to(ptm[0] + sin_a * length * self.W1, ptm[1] - cos_a * length * self.W1)
        if self.W2 is not None:
            cr.line_to(ptm[0] + sin_a * length * self.W2, ptm[1] - cos_a * length * self.W2)
        cr.line_to(*pte)
        if self.W2 is not None:
            cr.line_to(ptm[0] - sin_a * length * self.W2, ptm[1] + cos_a * length * self.W2)
        cr.line_to(ptm[0] - sin_a * length * self.W1, ptm[1] + cos_a * length * self.W1)
        cr.line_to(ptq[0] - sin_a * length * self.W1, ptq[1] + cos_a * length * self.W1)
        cr.close_path()
        cr.fill()
        cr.stroke()


class Cadran:
    def __init__(self):
        self.values = None
        self.graduations = []
        self.needles = []
        self.label_1 = None
        self.label_2 = None
        return

    def set_label_1(self, label):
        self.label_1 = label

    def set_label_2(self, label):
        self.label_2 = label

    # def add_graduation(self, grad):
    #    self.graduations.append(grad)

    # def add_needle(self):
    #    self.needles.append()
    #    pass

    def add(self, item):
        if type(item) == Aiguille:
            self.needles.append(item)
        elif type(item) in [ArcGradue]:
            self.graduations.append(item)
        else:
            print(f"Cadran.add(item) {type(item)} not in Aiguille, CercleGradue, ArcGradue", file=sys.stderr)
            pass
        return

    def set_value(self, values):
        # print(f"  ---> {values}")
        self.values = values

    def draw(self, cr, center_x, center_y, radius, color):
        # dessin des arcs gradués
        for g in self.graduations:
            g.draw(cr, center_x, center_y, radius, color)

        # Dessin de l'aiguille ou des aiguilles
        # print(f"Nombre d'aiguilles(s) : {len(self.needles)}")
        for ndl in self.needles:
            # print(f"  -- --> {self.values}")
            if self.values is not None:
                # angle = calculs.deg2rad(self.values)
                for grad in self.graduations:
                    angle = grad.get_angle(self.values)
                    if angle is not None:
                        ndl.set_angle(angle)
                        ndl.draw(cr, center_x, center_y, radius * 0.9, color)

        return


class Instrument(Gtk.Layout):
    def __init__(self, dashboard, config, queue_out):
        super().__init__()
        self.queue_out = queue_out
        self.middle_y = None
        self.middle_x = None
        self.dashboard = dashboard
        self.fore_color = dashboard.colors.get("fore")
        self.back_color = dashboard.colors.get("back")
        # self.title = title
        self.connect("draw", self.on_draw)
        self.width = None
        self.height = None
        self.center_x = None
        self.center_y = None
        self.min_dim = None
        self.max_dim = None
        self.radius = None
        self.size_changed = False

    def on_draw(self, widget, cr) -> None:
        # print("--> Instrument::on_draw()")

        # Initialize vars
        prop2 = 0.05  # Taille des chanfreins aux angles du rectangle, 0 à 0.5
        if self.width != self.get_allocated_width() and self.height != self.get_allocated_height():
            self.size_changed = True
        else:
            self.size_changed = False
        self.width = self.get_allocated_width()
        self.height = self.get_allocated_height()
        self.center_x = self.width / 2
        self.center_y = self.height / 2
        self.min_dim = min(self.width, self.height)
        self.max_dim = max(self.width, self.height)
        self.radius = self.min_dim * 0.35
        ecart = self.min_dim * prop2
        self.middle_x, self.middle_y = self.width / 2, self.height / 2

        # Clear drawing area, fill with foreground color
        cr.set_source_rgb(*self.back_color)
        cr.paint()
        cr.fill()

        # Draw a border
        cr.move_to(ecart, 2)
        cr.line_to(self.width - ecart, 1)
        cr.line_to(self.width - 2, ecart)
        cr.line_to(self.width - 2, self.height - ecart)
        cr.line_to(self.width - ecart, self.height - 2)
        cr.line_to(ecart, self.height - 2)
        cr.line_to(2, self.height - ecart)
        cr.line_to(2, ecart)
        cr.line_to(ecart, 2)
        cr.set_source_rgb(*self.fore_color)
        cr.set_line_width(3)
        cr.stroke()

        return

    def set_values(self, values):
        return

    def send_data(self, data):

        return

    @staticmethod
    def create_instrument(parent, config, queue_out):
        instrument = None
        if config["type"] == "compass":
            instrument = InstrumentHeading(parent, config, queue_out)
        elif config["type"] == "clock":
            instrument = InstrumentClock(parent, config, queue_out)
        elif config["type"] == "attitude":
            instrument = InstrumentAttitude(parent, config, queue_out)
        elif config["type"] == "wind":
            instrument = InstrumentWind(parent, config, queue_out)
        elif config["type"] == "speed":
            instrument = InstrumentCompteur(parent, config, queue_out)
        elif config["type"] == "autopilot":
            instrument = InstrumentAutoPilot(parent, config, queue_out)
        elif config["type"] == "autopilotdev":
            instrument = InstrumentAutoPilotDev(parent, config, queue_out)
        else:
            instrument = Instrument(parent, config, queue_out)

        """
        elif config["type"] == "wind":
            instrument = Instrument_Wind(parent, config)
        elif config["type"] == "APcontrol":
            instrument = Instrument_APcontrol(parent, config)
        elif config["type"] == "speed":
            instrument = Instrument_speed(parent, config)
        elif config["type"] == "tide":
            instrument = Instrument_Tide(parent, config)
        """

        return instrument


class InstrumentHeading(Instrument):
    def __init__(self, parent, config, queue_out):
        super().__init__(parent, config, queue_out)
        self.values = None
        self.r1, self.r2 = None, None
        self.needle = Aiguille("HDG")
        # math and cairo libs count counterclockwise from x axis
        self.displayed_values = ["E", "6", "3", "N", "33", "30", "W", "24", "21", "S", "15", "12"]

    def set_values(self, values):
        # print("InstrumentHeading : set_values(", values, ")")
        if values.type == "ATTITUDE":
            # print (f"Instrument Heading {values.get_heading()}")
            self.values = values.get_heading()
        self.queue_draw()

    def on_draw(self, widget, cr) -> None:
        super().on_draw(widget, cr)
        self.radius = self.min_dim * 0.94 * 0.5
        self.r_grad = self.radius * 0.75
        self.r_grad_5 = self.radius * 0.80
        self.r_grad_10 = self.radius * 0.85
        self.r_labels = self.radius * 0.85

        cr.set_source_rgb(*self.fore_color)

        # dessin du cercle extérieur
        # Désactivé
        cr.set_line_width(self.radius * 0.02)
        cr.move_to(self.center_x + self.radius, self.center_y)
        cr.arc(self.center_x, self.center_y, self.radius, 0, math.pi * 2.)
        cr.stroke()

        # dessin du cercle intérieur
        cr.set_line_width(self.radius * 0.02)
        cr.move_to(self.center_x + self.r_grad, self.center_y)
        cr.arc(self.center_x, self.center_y, self.r_grad, 0, math.pi * 2.)
        cr.stroke()

        cr.set_font_size(int(self.radius / 10))
        # Dessin des graduations
        for i in range(0, 360, 5):
            angle = i * (math.pi / 180)
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)

            # 3 cas : multiple de 30 graduation courte et large
            #         pas multiple de 30 mais de 10 graduation large te courte
            #         sinon graduation courte et fine
            if i % 30 == 0:
                cr.set_line_width(self.radius * 0.02)
                cr.move_to(self.center_x + cos_a * self.r_grad_5,
                           self.center_y + sin_a * self.r_grad_5)

            elif i % 10 == 0:
                cr.set_line_width(self.radius * 0.02)
                cr.move_to(self.center_x + cos_a * self.radius,
                           self.center_y + sin_a * self.radius)

            else:
                cr.set_line_width(self.radius * 0.01)
                cr.move_to(self.center_x + cos_a * self.r_grad_5,
                           self.center_y + sin_a * self.r_grad_5)

            cr.line_to(self.center_x + cos_a * self.r_grad,
                       self.center_y + sin_a * self.r_grad)
            cr.stroke()

            """
            if i% 6 :
                label = self.displayed_values[i/6]
                text_extents = cr.text_extents(label)
                cr.move_to(self.center_x + self.r_labels * cos_a, self.center_y + self.r_labels * sin_a)
                cr.show_text(label)
            """

        # Dessin des valeurs
        # choix de la police et de sa taille
        cr.set_font_size(int(self.radius / 6))
        for ilbl in range(len(self.displayed_values)):
            angle = ilbl * 30. * (math.pi / 180.)
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            label = self.displayed_values[ilbl]
            text_extents = cr.text_extents(label)

            cr.save()
            # cr.translate(self.center_x + self.r_labels*cos_a, self.center_y - self.r_labels*sin_a)
            cr.translate(self.center_x + self.r_labels * cos_a,
                         self.center_y - self.r_labels * sin_a)
            text_extents = cr.text_extents(label)
            cr.rotate(-angle + math.pi / 2)
            cr.move_to(-text_extents.width / 2., 0)
            cr.show_text(label)
            cr.restore()

        # self.draw_values(widget, cr)
        self.needle.set_angle(self.values)
        self.needle.draw(cr, self.center_x, self.center_y, self.r_grad, self.fore_color)

    # def draw_values(self, widget, cr) -> None:
    #    self.needle.set_angle(self.values)
    #    self.needle.draw(cr, self.center_x, self.center_y, self., self.values)


class InstrumentAttitude(Instrument):
    def __init__(self, parent, config, queue_out):
        super().__init__(parent, config, queue_out)
        self.values = None
        self.roll = None
        self.pitch = None
        self.last_values_time = 0
        self.values_available = False

    def on_draw(self, widget, cr):
        # print("Instrument Compteur :: on_draw()")
        super().on_draw(widget, cr)
        self.radius = self.min_dim * 0.45

        cr.set_source_rgb(*self.fore_color)

        # Dessin du cercle extérieur
        cr.set_line_width(self.radius * 0.02)
        cr.move_to(self.center_x + self.radius, self.center_y)
        cr.arc(self.center_x, self.center_y, self.radius, 0, math.pi * 2.)
        cr.stroke()

        # Dessin du cercle intérieur, à activer si besoin
        # cr.set_line_width(self.radius * 0.005)
        # cr.move_to(self.center_x + self.radius * 0.9, self.center_y)
        # cr.arc(self.center_x, self.center_y, self.radius * 0.9, 0, math.pi * 2.)

        # Dessin des graduations de roulis
        # cr.set_line_width(self.radius * 0.02)
        for i in range(13):
            angle = - ((i + 3) * math.pi / 18)
            cr.set_line_width(self.radius * 0.03 if i % 3 == 0 else self.radius * 0.01)
            cr.move_to(self.center_x + self.radius * 0.9 * math.cos(angle),
                       self.center_y + self.radius * 0.9 * math.sin(angle))
            cr.line_to(self.center_x + self.radius * math.cos(angle),
                       self.center_y + self.radius * math.sin(angle))
            cr.stroke()

        # self.draw_values(widget, cr)

        # def draw_values(self, widget, cr):
        if self.roll is not None and self.pitch is not None:
            angle_diag = 42. * math.pi / 180.
            cos_a = math.sin(angle_diag + self.roll)
            sin_a = math.sin(angle_diag + self.roll)

            #         |                  <-- needle to arc
            # tl------------------tr
            #  |   bright  blue   |      <-- sky
            # hl------------------hr
            # |    dark blue      |       <-- water (ground and brown in a plane)
            # bl------------------br

            # angle haut à gauche
            tl = (self.center_x - self.radius * 0.9 * math.cos(self.roll + angle_diag),
                  self.center_y - self.radius * 0.9 * math.sin(self.roll + angle_diag))

            # Angle en, haut à droite
            tr = (self.center_x + self.radius * 0.9 * math.cos(-self.roll + angle_diag),
                  self.center_y - self.radius * 0.9 * math.sin(-self.roll + angle_diag))
            # tr = (self.middle_x,self.middle_y)

            # Angle en bas à droite
            br = (self.center_x + self.radius * 0.9 * math.cos(self.roll + angle_diag),
                  self.center_y + self.radius * 0.9 * math.sin(self.roll + angle_diag))

            # Angle en bas à droite
            bl = (self.center_x - self.radius * 0.9 * math.cos(-self.roll + angle_diag),
                  self.center_y + self.radius * 0.9 * math.sin(-self.roll + angle_diag))

            # Extrémité gauche de l'horizon
            hl = (bl[0] + (tl[0] - bl[0]) * (1.0 + math.sin(self.pitch)) * 0.5,
                  bl[1] + (tl[1] - bl[1]) * (1.0 + math.sin(self.pitch)) * 0.5)

            # Extrémité droite de l'horizon
            hr = (br[0] + (tr[0] - br[0]) * (1.0 + math.sin(self.pitch)) * 0.5,
                  br[1] + (tr[1] - br[1]) * (1.0 + math.sin(self.pitch)) * 0.5)

            for i in range(-3, 4, 1):
                pass

            # Dessin du triangle indiquant le roulis
            cr.set_source_rgb(*self.fore_color)
            cr.move_to(self.center_x + self.radius * 0.9 * math.cos(self.roll - math.pi * 0.5),
                       self.center_y + self.radius * 0.9 * math.sin(self.roll - math.pi * 0.5))
            cr.line_to(self.center_x + self.radius * 0.7 * math.cos(self.roll - math.pi * 0.54),
                       self.center_y + self.radius * 0.7 * math.sin(self.roll - math.pi * 0.54))
            cr.line_to(self.center_x + self.radius * 0.7 * math.cos(self.roll - math.pi * 0.46),
                       self.center_y + self.radius * 0.7 * math.sin(self.roll - math.pi * 0.46))
            # cr.line_to(self.center_x + self.radius * 0.9 * math.cos(self.roll - math.pi * 0.5),
            #           self.center_y + self.radius * 0.9 * math.sin(self.roll - math.pi * 0.5))
            cr.close_path()
            cr.fill()

            # dessin du bord de la fenêtre
            cr.move_to(*tl)
            cr.line_to(*tr)
            cr.line_to(*br)
            cr.line_to(*bl)
            cr.line_to(*tl)
            cr.close_path()
            cr.stroke()

            # Dessin du trait d'horizon
            cr.move_to(*hl)
            cr.line_to(*hr)
            cr.stroke()

            # dessin du ciel
            cr.set_source_rgb(0.2, 0.4, 1)
            cr.move_to(*tr)
            cr.line_to(*tl)
            cr.line_to(*hl)
            cr.line_to(*hr)
            cr.fill()

            # dessin de la mer
            cr.set_source_rgb(0.0, 0.0, 0.4)
            cr.move_to(*br)
            cr.line_to(*bl)
            cr.line_to(*hl)
            cr.line_to(*hr)
            cr.fill()

        # Dessin de la représentation du navire
        # Ici c'est une couleur spéciale
        cr.set_source_rgb(1.0, 0.7, 0.1)
        cr.set_line_width(self.radius * 0.04)
        cr.move_to(self.center_x + self.radius * 0.5, self.center_y)
        cr.line_to(self.center_x + self.radius * 0.1, self.center_y)
        cr.arc(self.center_x, self.center_y, self.radius * 0.1, 0, math.pi)
        cr.line_to(self.center_x - self.radius * 0.5, self.center_y)
        cr.stroke()

        # Affichage d'un drapeau de données indisponibles le cas échéant
        # print(f"Disponibilité {self.values_available}")
        if self.values_available == False:
            cr.set_source_rgb(0.9, 0.1, 0.2)
            cr.move_to(self.width * 0.05, self.height * 0.05)
            cr.line_to(self.width * 0.20, self.height * 0.05)
            cr.line_to(self.width * 0.20, self.height * 0.20)
            cr.line_to(self.width * 0.05, self.height * 0.20)
            cr.close_path()
            cr.fill()

    def set_values(self, values):

        if values.type == "ATTITUDE":
            self.last_values_time = values.timestamp
            self.values = values
            self.pitch = values.get_pitch()
            self.roll = values.get_roll()
            self.queue_draw()

        if values.type == "SysTime":
            if values.timestamp - self.last_values_time > 2:
                self.values_available = False
                # print(f"Perte information")
                self.queue_draw()
            else:
                self.values_available = True
                # print(f"Information disponible")
            pass


class InstrumentClock(Instrument):
    """
    Horloge à afficher sur le tableau de bord.
    """

    def __init__(self, parent, config, queue_out):
        super().__init__(parent, config, queue_out)
        self.time = None
        self.title = config.get("title")
        self.time_zone = config.get("time_zone")

    def set_timezone(self, time_zone):
        self.time_zone = time_zone
        self.queue_draw()

    def set_values(self, values):
        # print(f"--> InstrumentClock.set_values {values}")
        if values.type == "SysTime":
            self.time = values.get_timestamp()
            self.queue_draw()
        return

    def on_draw(self, widget, cr):
        # print("Instrument Clock :: on_draw()")
        super().on_draw(widget, cr)

        width = self.get_allocated_width()
        height = self.get_allocated_height()
        radius = min(width, height) * 0.35
        cr.set_source_rgb(*self.back_color)
        cr.paint()
        cr.translate(width / 2, height / 2)

        cr.set_font_size(int(radius / 5))
        self.draw_clock_face(cr, radius)
        self.draw_values(cr, radius)

        # Draw title
        cr.set_font_size(int(radius / 5))
        text_extents = cr.text_extents(self.title)
        cr.move_to(- text_extents.width / 2, -((height * 0.50) - text_extents.height * 1.5))
        cr.show_text(self.title)

    def draw_clock_face(self, cr, radius):
        cr.set_source_rgb(*self.fore_color)
        cr.set_line_width(2)
        for i in range(60):
            angle = i * 6
            angle_radians = math.radians(angle)
            outer_x = (radius + 10) * math.cos(angle_radians)
            outer_y = (radius + 10) * math.sin(angle_radians)
            if i % 5 == 0:
                cr.set_line_width(2)
                inner_x = (radius - 10) * math.cos(angle_radians)
                inner_y = (radius - 10) * math.sin(angle_radians)
            else:
                cr.set_line_width(1)
                inner_x = radius * math.cos(angle_radians)
                inner_y = radius * math.sin(angle_radians)
            cr.move_to(inner_x, inner_y)
            cr.line_to(outer_x, outer_y)
            cr.stroke()

    def draw_values(self, cr, radius):

        if self.time is not None:

            height = self.get_allocated_height()

            tz = pytz.timezone(self.time_zone)
            time_to_display = datetime.datetime.fromtimestamp(self.time, tz)

            hours = time_to_display.hour % 12
            minutes = time_to_display.minute
            seconds = time_to_display.second

            # Draw Text Time
            if self.time is not None:
                time_str = time_to_display.strftime("%H:%M:%S")
                text_extents = cr.text_extents(time_str)
                cr.move_to(- text_extents.width / 2, +((height * 0.40) + text_extents.height * 1.5))
                cr.show_text(time_str)

            # Draw hour hand
            self.draw_hand(cr, radius * 0.5, (hours + minutes / 60) * 30 - 90, 6)
            # Draw minute hand
            self.draw_hand(cr, radius * 0.8, (minutes + seconds / 60) * 6 - 90, 3)
            # Draw second hand
            self.draw_hand(cr, radius * 0.9, seconds * 6 - 90, 2, True)

            # Draw digital time
            time_str = time_to_display.strftime("%H:%M:%S")
            # self.draw_text(cr, time_str, -radius * 0.5, radius + 20, 20)
            cr.set_source_rgb(*self.fore_color)

            # self.draw_text(cr, time_str, -radius * 0.5, radius + 20, 20)
            # self.draw_text(cr, time_str, 100, 100, 20)

    def draw_hand(self, cr, length, angle, width, is_second_hand=False):
        angle_radians = math.radians(angle)
        x = length * math.cos(angle_radians)
        y = length * math.sin(angle_radians)

        cr.set_line_width(width)
        if is_second_hand:
            cr.set_source_rgb(1, 0, 0)  # Red for second hand
        else:
            cr.set_source_rgb(*self.fore_color)

        cr.move_to(0, 0)
        cr.line_to(x, y)
        cr.stroke()


class InstrumentWind(Instrument):
    def __init__(self, parent, config, queue_out):
        super().__init__(parent, config, queue_out)
        # print(f"InstrumentWind.__init__()")
        self.value = None

        self.cadran_circle = Cadran()
        self.cercle = ArcGradue(ArcGradue.CIRCLE, min_value=-270, max_value=90)
        # [x**2 for x in range(10)]
        self.cercle.set_ticks([(angle, f"{angle:2d}") for angle in range(30, 390, 30)])
        self.cercle.add_zone(0, 180, (0, 0.8, 0))
        self.cercle.add_zone(180, 360, (1, 0, 0))
        self.cadran_circle.add(self.cercle)
        self.cadran_circle.add(Aiguille("THIN"))

        self.cadran_closed_haul = Cadran()
        self.arc_stbd = ArcGradue(ArcGradue.ARC, calculs.deg2rad(20), calculs.deg2rad(150), 30, 60)
        self.arc_port = ArcGradue(ArcGradue.ARC, calculs.deg2rad(-150), calculs.deg2rad(-20), -60, -30)
        self.arc_stbd.set_ticks([(30, "30"), (40, "40"), (50, "50"), (60, "60")])
        self.arc_port.set_ticks([(-30, "30"), (-40, "40"), (-50, "50"), (-60, "60")])
        self.arc_stbd.add_zone(30, 60, (0, 0.8, 0))
        self.arc_port.add_zone(-60, -30, (1, 0, 0))
        self.cadran_closed_haul.add(self.arc_stbd)
        self.cadran_closed_haul.add(self.arc_port)
        self.cadran_closed_haul.add(Aiguille("THIN"))

        self.mode_closed_haul = False

        self.fixed = Gtk.Fixed()
        self.add(self.fixed)
        self.button = Gtk.Button(label="Mode")
        self.fixed.add(self.button)
        self.button.connect("clicked", self.mode_toggle)

    def mode_toggle(self, widget):
        self.mode_closed_haul = False if self.mode_closed_haul else True
        print(f"Changement de mode : {self.mode_closed_haul}")
        self.queue_draw()

    def on_draw(self, widget, cr):
        super().on_draw(widget, cr)

        if self.size_changed:
            # self.button.set_size_request()

            # Créer un objet Pango.FontDescription
            font_desc = Pango.FontDescription()
            font_desc.set_family("Arial")  # Choisir la famille de polices (ex. Arial)
            font_desc.set_size(self.min_dim * 0.04 * Pango.SCALE)  # Définir la taille en points (ici 20 points)
            # font_desc.set_style(Pango.Style.ITALIC)  # Définir le style (ITALIQUE)
            # font_desc.set_weight(Pango.Weight.BOLD)  # Définir le poids (GRAS)

            # Appliquer la police au bouton
            self.button.modify_font(font_desc)
            # self.button.set_property("halign", Gtk.Align.FILL)
            # self.button.set_property("valign", Gtk.Align.FILL)

            # print(f"InstrumentWind : changement de taille")
            # self.fixed.move(self.button, self.width * 0.10, self.height * 0.8)
            # self.button.set_size_request(self.width * 0.05, self.height * 0.03)
            # self.button.set_size_request(0., 0.)

            self.fixed.move(self.button, int(self.min_dim * .05), int(self.min_dim * .05))
            self.button.set_size_request(self.width * 0.1, self.height * 0.1)
        # if self.size_changed

        # Calcul de valeurs utilisées par le dessin
        width = self.get_allocated_width()
        height = self.get_allocated_height()
        middle_x, middle_y = width / 2, height / 2
        radius = 0.45 * min(width, height)

        # dessin du cadran
        if self.mode_closed_haul:
            self.cadran_closed_haul.draw(cr, middle_x, middle_y, radius, self.fore_color)
            pass
        else:  # mode circular / 360 deg.
            self.cadran_circle.draw(cr, middle_x, middle_y, radius, self.fore_color)

    def set_values(self, values):
        """
        Affichage de données de vent.
        :param values: Vent à afficher force et direction
        :type a: data.DataWind
        :returns: Nothing
        """
        # print(f"Vent : réception de valeur {type(values)}")
        if type(values) == data.DataWind:
            # print(f"Vent : réception de  {str(values)}")
            if self.mode_closed_haul:
                self.cadran_closed_haul.set_value(values.get_direction())
            else:
                self.cadran_circle.set_value(values.get_direction())
            self.queue_draw()
        pass


class InstrumentAutoPilotDev(Instrument):
    def __init__(self, parent, config, queue_out):
        super().__init__(parent, config, queue_out)
        self.last_values_time = None
        self.layout = Gtk.Fixed()
        self.add(self.layout)

        self.info_text = Gtk.TextView()
        self.layout.put(self.info_text, 1, 1)
        self.info_text.set_editable(False)
        self.info_text.set_wrap_mode(Gtk.WrapMode.WORD)
        # self.buffer_text = self.info_text.get_buffer()
        # self.buffer_text.set_text("Nauteff !")
        self.infoap = {"Current gap": "?", "Integrated gap": "?", "Command" : "?"}

        self.param_text = Gtk.TextView()
        self.layout.put(self.param_text, 1, 1)
        self.param_text.set_editable(True)
        self.param_text.set_wrap_mode(Gtk.WrapMode.WORD)
        self.paramap = "coefficient proportional 1\ncoefficient integral 2\ncoefficient derivative 3"
        self.param_buffer_text = self.param_text.get_buffer()
        self.param_buffer_text.set_text(self.paramap)
        self.btn_apply = Gtk.Button(label="Apply")
        self.layout.put(self.btn_apply, 0, 0)
        self.btn_apply.connect("clicked", self.on_clic, "apply")

    def on_draw(self, widget, cr) -> None:
        super().on_draw(widget, cr)

        self.info_text.set_size_request(self.width * 0.8, self.height * 0.3)
        self.layout.move(self.info_text, self.width * 0.1, self.height * 0.10)

        self.param_text.set_size_request(self.width * 0.8, self.height * 0.3)
        self.layout.move(self.param_text, self.width * 0.1, self.height * 0.50)

        self.btn_apply.set_size_request(self.width * 0.2, self.height * 0.1)
        self.layout.move(self.btn_apply, self.width * 0.7, self.height * 0.8)

    def set_values(self, values):

        if values.type == "APINFO":
            self.last_values_time = values.timestamp
            try:
                s = values.initialFrame.upper().split()
                if (s[0] == "AP"):
                    if s[1] == "GAP":
                        if s[2] is not None:
                            self.infoap["Current gap"] = s[2]
                            if s[3] is not None:
                                self.infoap["Integrated gap"] = s[3]
                                if s[3] is not None:
                                    self.infoap["Command"] = s[4]
            except:
                pass

        textinfo = ""

        for key, val in self.infoap.items():
            textinfo += f"{key:16s} : {val}\n"
        # textinfo = textinfo[:-1]

        buffer = self.info_text.get_buffer()
        buffer.set_text(textinfo)

        self.queue_draw()

        return

    def on_clic(self, button, textcmd):

        buffer = self.param_text.get_buffer()

        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()
        text = buffer.get_text(start_iter, end_iter, False)

        for prm in text.splitlines():
            print("Application de paramètres", prm)
            cmd = data.dataAPCommand(time.time(), prm, "Dashboard")
            self.queue_out.put(cmd)

        return


class InstrumentAutoPilot(Instrument):
    """
    Interface for autopilot.
    It sends commands to autopilot :
    - Auto : mode heading ;
    - Idle : mode idle
    - -1 : turn port 1
    - +1 : turn starboard 1
    - -10 : turn port 10
    - +10 : turn starboard 10
    """

    def __init__(self, parent, config, queue_out):
        super().__init__(parent, config, queue_out)
        self.motor = None
        self.last_values_time = None
        self.heading = None

        self.layout = Gtk.Fixed()
        self.add(self.layout)
        print(f"Taille {self.width} x {self.height} ")

        # création de la zone de texte
        self.info_text = Gtk.TextView()
        self.info_text.set_editable(False)
        self.info_text.set_wrap_mode(Gtk.WrapMode.WORD)
        self.buffer_text = self.info_text.get_buffer()
        self.buffer_text.set_text("Nauteff !")

        btnscmd = ["mode heading", "mode idle", "turn port 1",
                   "turn starboard 1", "turn port 10", "turn starboard 10"]
        # Création des boutons
        self.btnAuto = Gtk.Button(label="Auto")
        self.btnIdle = Gtk.Button(label="Idle")
        self.btnMinusOne = Gtk.Button(label="- 1")
        self.btnPlusOne = Gtk.Button(label="+ 1")
        self.btnMinusTen = Gtk.Button(label="- 10")
        self.btnPlusTen = Gtk.Button(label="+ 10")
        self.buttons = [self.btnAuto, self.btnIdle, self.btnMinusOne, self.btnPlusOne, self.btnMinusTen,
                        self.btnPlusTen]
        self.textinfo = Gtk.TextView()
        self.textinfo.set_editable(False)
        self.infoap = {"Mode": "?", "Steer": "None", "AHRS": "?", "Heading": "?", "Roll": "?", "Pitch": "?"}

        idx = 0
        for btn in self.buttons:
            self.layout.put(btn, 0, 0)
            btn.connect("clicked", self.on_clic, btnscmd[idx])
            idx += 1
        self.layout.put(self.textinfo, 5, 5)

    def set_values(self, values):

        if values.type in ["APINFO", "ATTITUDE"]:
            # print(f"Instrument AP | MOTOR : {values.initialFrame}")
            self.last_values_time = values.timestamp
            try:
                s = values.initialFrame.upper().split()

                if (s[1] == "HEADING") and (s[2] == "GAP"):
                    print(f" --> Heading gap {s[3]}")

                if s[0] == "ATTITUDE":
                    try:
                        hdg = float(s[1])
                        roll = float(s[2])
                        pitch = float(s[3])
                        self.infoap["Heading"] = hdg
                        self.infoap["Roll"] = roll
                        self.infoap["Pitch"] = pitch
                    except:
                        self.infoap["Heading"] = "?"
                        self.infoap["Roll"] = "?"
                        self.infoap["Pitch"] = "?"

                if s[0] == "MOTOR":
                    if s[1] == "TURN":
                        if s[2] in ["PORT", "STARBOARD"]:
                            self.motor = s[2]
                        else:
                            self.motor = "?"
                    elif s[1] == "STOPPED":
                        self.motor = s[1]

                if s[0] == "AP":
                    if s[1] == "MODE":
                        if s[2] == "IDLE":
                            self.infoap["Mode"] = "Idle"
                        elif s[2] == "HEADING":
                            self.infoap["Mode"] = "Heading"
                        else:
                            self.infoap["Mode"] = "?"

                    if s[1] == "AHRS":
                        self.infoap["AHRS"] = s[2]
            except:
                pass

            textinfo = ""
            for key, val in self.infoap.items():
                textinfo += f"{key:10s} : {val}\n"
            if textinfo[-1] == "\n":
                textinfo = textinfo[:-1]

            buffer = self.textinfo.get_buffer()
            buffer.set_text(textinfo)

    def on_clic(self, button, txtcmd):
        """
        on_clic is called when en button is pressed.
        It makes a dataAPCommand  with the text in textcmd
        and sends it to the main queue.
        """
        print("Commande : ", button.get_label(), txtcmd)
        self.buffer_text.set_text(txtcmd)
        cmd = data.dataAPCommand(time.time(), txtcmd, "Dashboard")
        self.queue_out.put(cmd)

    def on_draw(self, widget, cr):
        super().on_draw(widget, cr)

        # buttonWidth = int(self.width * 0.25)
        # buttonHeight = int(self.height * 0.10)
        i = 0
        for btn in self.buttons:
            x, y = int(self.width * (0.1 + (i % 2) * 0.6)), int(self.middle_y + self.height * (i // 2) * 0.15)
            btn.set_size_request(self.width * 0.25, self.height * 0.1)
            self.layout.move(btn, x, y)
            # btn.modify_font(self.)
            i += 1

            # x, y = int(self.width * (0.1 + (i % 2) * 0.6)), int(self.middle_y + self.height * (i // 2) * 0.15)
            # btn.set_size_request(self.width * 0.25, self.height * 0.1)
            # self.layout.move(btn, x, y)
        self.textinfo.set_size_request(self.width * 0.8, self.height * 0.3)
        self.layout.move(self.textinfo, self.width * 0.1, self.height * 0.15)

        if self.motor == "STOPPED":
            cr.set_source_rgb(0.1, 0.1, 0.1)
        elif self.motor == "STARBOARD":
            cr.set_source_rgb(0.0, 0.9, 0.0)
        elif self.motor == "PORT":
            cr.set_source_rgb(0.9, 0.1, 0.0)
        else:
            cr.set_source_rgb(0.3, 0.3, 0.3)
        cr.move_to(self.width * 0.80, self.height * 0.05)
        cr.line_to(self.width * 0.95, self.height * 0.05)
        cr.line_to(self.width * 0.95, self.height * 0.20)
        cr.line_to(self.width * 0.80, self.height * 0.20)
        cr.close_path()
        cr.fill()


class InstrumentCompteur(Instrument):
    def __init__(self, parent, config, queue_out):
        # print(f"--> Compteur : {config}")
        super().__init__(parent, config, queue_out)
        self.cadran = Cadran()
        self.compteur = 0
        self.start_angle = calculs.deg2rad(-180. + 45.)
        self.end_angle = calculs.deg2rad(180. - 45.)
        self.value = None
        self.min_val = config.get("min_val") if config.get("min_val") is not None else 0
        self.max_val = config.get("max_val") if config.get("max_val") is not None else 10
        self.arc = ArcGradue(ArcGradue.ARC,
                             self.start_angle, self.end_angle,
                             self.min_val, self.max_val)
        # self.arc.set_ticks([(0, "0"), (2, "2"), (4, "4"), (6, "6"), (8, "8"), (10, "10")])
        self.arc.set_ticks(gen_ticks(self.min_val, self.max_val))
        self.cadran.add(self.arc)

    def on_draw(self, widget, cr):
        # print("Instrument Compteur :: on_draw()")
        super().on_draw(widget, cr)

        # Calcul de valeurs utilisées par le dessin
        width = self.get_allocated_width()
        height = self.get_allocated_height()
        middle_x, middle_y = width / 2, height / 2
        radius = 0.45 * min(width, height)

        # Dessin du fond en couleur d'arrière-plan
        # cr.set_source_rgb(*self.back_color)
        # cr.paint()
        # cr.fill()

        # dessin du cadran
        self.compteur += 1
        self.cadran.draw(cr, middle_x, middle_y, radius, self.fore_color)

        # Affichage du dessin
        # cr.stroke()

    def set_value(self, value):
        if type(value) == data.DataWind:
            self.value = value
            self.cadran.set_value(value)
            self.queue_draw()


class CommandBoard(Gtk.Box):
    """
    A command board  for the dashboard.
    It contains 2 buttons and a editable text zone.
    The button "mark" store a timestamp when pressed.
    The button record send a log messsage whith the text in text zone and a time stamp.
    it resets the timestamp.
    if a timestamp is stored the record contains this timestamp otherwise it is
    the timstamp of the recod press.
    """

    def __init__(self, dashboard, config=None):
        super().__init__()

        self.dashboard = dashboard

        self.mark_time = None  # the time the "mark" button is pressed

        # Button "Marque" creation, first left
        self.btn_marque = Gtk.Button(label='Mark')
        self.pack_start(self.btn_marque, False, True, 0)
        self.btn_marque.connect("clicked", self.on_marque)

        # Entry text for message, center, as large as possible
        self.entry_message = Gtk.Entry()
        self.pack_start(self.entry_message, True, True, 0)

        self.btn_enregistre = Gtk.Button(label='Record')
        self.pack_start(self.btn_enregistre, False, False, 0)
        self.btn_enregistre.connect("clicked", self.on_marque)

    def on_marque(self, widget):
        if widget == self.btn_marque:
            self.mark_time = time.time()
            # print(f"Marque")
        if widget == self.btn_enregistre:
            message = self.entry_message.get_text()
            if message != "":
                if self.mark_time is None:
                    self.mark_time = time.time()
                # print(f"Enregistre {self.entry_message.get_text()}  {self.mark_time}")
                data_log = data.dataLog(self.mark_time, "Dashboard", self.entry_message.get_text())
                self.dashboard.queue_out.put(data_log)
                self.entry_message.set_text("")
                self.mark_time = None

        return


class Dashboard(data.DataInterface, ABC):
    def __init__(self, config, queue_out):
        super().__init__(config, queue_out)

        self.instruments = []

        self.main_window = Gtk.Window(title="Dashboard")
        self.main_window.set_default_size(800, 600)
        self.colors = {"fore": (1, 1, 1), "back": (0, 0, 0)}

        # main box : top and max size instruments in instr_grid,
        # bottom cmd_box for commands
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.instr_grid = Gtk.Grid()
        self.instr_grid.set_column_homogeneous(True)
        self.instr_grid.set_row_homogeneous(True)

        for id_instr, desc_instr in config.get("instruments").items():
            # print(f"Ajout : {id_instr:12s} {desc_instr.get('type')}")
            instrument = Instrument.create_instrument(self, desc_instr, self.queue_out)
            self.instr_grid.attach(instrument,
                                   desc_instr.get("cell_origx"),
                                   desc_instr.get("cell_origy"),
                                   desc_instr.get("cell_width"),
                                   desc_instr.get("cell_height"))
            self.instruments.append(instrument)

        self.command_board = CommandBoard(self, self.config)

        self.main_box.pack_start(self.instr_grid, True, True, 0)
        self.main_box.pack_start(self.command_board, False, True, 0)

        self.main_window.add(self.main_box)
        self.main_window.connect("destroy", Gtk.main_quit)

        return

    def put_data(self, values):
        GLib.idle_add(self.put_data_threaded, values)

    def put_data_threaded(self, values):
        # print(f"tableau de bord reçoit : {data.str4log()}")
        if self.ready:
            for instr in self.instruments:
                instr.set_values(values)
        return 0

    def get_data_list_in(self) -> list:
        return []

    def get_data_list_out(self):
        return []

    def terminate(self) -> None:
        return

    def run(self) -> None:
        self.main_window.show_all()
        self.ready = True
        Gtk.main()
        self.ready = False
        self.queue_out.put("Terminate")

        pass
