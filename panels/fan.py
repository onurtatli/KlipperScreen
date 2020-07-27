import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

from KlippyGtk import KlippyGtk
from KlippyGcodes import KlippyGcodes
from screen_panel import ScreenPanel

class FanPanel(ScreenPanel):
    def initialize(self, panel_name):
        # Create gtk items here
        grid = KlippyGtk.HomogeneousGrid()

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box.set_hexpand(True)

        adj = Gtk.Adjustment(0, 0, 100, 1, 5, 0)
        self.labels["scale"] = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adj)
        self.labels["scale"].set_digits(0)
        self.labels["scale"].set_hexpand(True)
        self.labels["scale"].connect("value-changed", self.set_fan_speed)
        self.labels["scale"].get_style_context().add_class("fan_slider")
        box.add(self.labels["scale"])

        self.labels["fanoff"] = KlippyGtk.ButtonImage("fan-off", "Fan Off")
        self.labels["fanoff"].get_style_context().add_class("color1")
        self.labels["fanoff"].connect("clicked", self.set_fan_on, False)
        self.labels["fanon"] = KlippyGtk.ButtonImage("fan", "Fan On")
        self.labels["fanon"].get_style_context().add_class("color3")
        self.labels["fanon"].connect("clicked", self.set_fan_on, True)

        grid.attach(box, 0, 0, 4, 2)
        grid.attach(self.labels["fanoff"], 0, 2, 1, 1)
        grid.attach(self.labels["fanon"], 1, 2, 1, 1)

        b = KlippyGtk.ButtonImage('back', 'Back')
        b.connect("clicked", self._screen._menu_go_back)
        grid.attach(b,3,2,1,1)

        self.panel = grid

    def set_fan_speed(self, widget):
        self._screen._ws.send_method("post_printer_gcode_script", {"script": KlippyGcodes.set_fan_speed(self.labels['scale'].get_value())})

    def set_fan_on(self, widget, fanon):
        speed = 100 if fanon == True else 0
        self.labels["scale"].set_value(speed)
        self._screen._ws.send_method("post_printer_gcode_script", {"script": KlippyGcodes.set_fan_speed(speed)})
