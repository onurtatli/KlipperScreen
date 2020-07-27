import gi
import os

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

from KlippyGtk import KlippyGtk
from KlippyGcodes import KlippyGcodes
from screen_panel import ScreenPanel

class SystemPanel(ScreenPanel):
    def initialize(self, panel_name):
        # Create gtk items here

        grid = KlippyGtk.HomogeneousGrid()

        restart = KlippyGtk.ButtonImage('reboot','Klipper Restart','color1')
        firmrestart = KlippyGtk.ButtonImage('restart','Firmware Restart','color2')
        back = KlippyGtk.ButtonImage('back', 'Back')
        back.connect("clicked", self._screen._menu_go_back)

        info = Gtk.Box()
        info.set_vexpand(True)

        title = Gtk.Label("System Information")
        title.set_margin_bottom(5)
        title.set_margin_top(15)

        lavg = os.getloadavg()
        loadavg = Gtk.Label("Load Average: %.2f %.2f %.2f" % (lavg[0], lavg[1], lavg[2]))

        title.get_style_context().add_class('temperature_entry')
        loadavg.get_style_context().add_class('temperature_entry')

        info.add(title)
        info.add(loadavg)


        grid.attach(info, 0, 0, 4, 2)
        grid.attach(restart, 0, 2, 1, 1)
        grid.attach(firmrestart, 1, 2, 1, 1)
        grid.attach(back, 3, 2, 1, 1)

        self.panel = grid
