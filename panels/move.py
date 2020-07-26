import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

from KlippyGtk import KlippyGtk
from KlippyGcodes import KlippyGcodes

class MovePanel:
    _screen = None
    labels = {}
    distance = 1
    distances = ['.1','.5','1','5','10','25']


    def __init__(self, screen):
        self._screen = screen


    def initialize(self, panel_name):

        grid = KlippyGtk.HomogeneousGrid()

        self.labels['x+'] = KlippyGtk.ButtonImage("move-x+", "X+", "color1")
        self.labels['x+'].connect("clicked", self.move, "X", "+")
        self.labels['x-'] = KlippyGtk.ButtonImage("move-x-", "X-", "color1")
        self.labels['x-'].connect("clicked", self.move, "X", "-")

        self.labels['y+'] = KlippyGtk.ButtonImage("move-y+", "Y+", "color2")
        self.labels['y+'].connect("clicked", self.move, "Y", "+")
        self.labels['y-'] = KlippyGtk.ButtonImage("move-y-", "Y-", "color2")
        self.labels['y-'].connect("clicked", self.move, "Y", "-")

        self.labels['z+'] = KlippyGtk.ButtonImage("move-z-", "Z+", "color3")
        self.labels['z+'].connect("clicked", self.move, "Z", "+")
        self.labels['z-'] = KlippyGtk.ButtonImage("move-z+", "Z-", "color3")
        self.labels['z-'].connect("clicked", self.move, "Z", "-")

        self.labels['home'] = KlippyGtk.ButtonImage("home", "Home All")
        self.labels['home'].connect("clicked", self.home)


        grid.attach(self.labels['x+'], 0, 1, 1, 1)
        grid.attach(self.labels['x-'], 2, 1, 1, 1)
        grid.attach(self.labels['y+'], 1, 0, 1, 1)
        grid.attach(self.labels['y-'], 1, 1, 1, 1)
        grid.attach(self.labels['z+'], 3, 0, 1, 1)
        grid.attach(self.labels['z-'], 3, 1, 1, 1)

        grid.attach(self.labels['home'], 0, 0, 1, 1)

        distgrid = Gtk.Grid()
        j = 0;
        for i in self.distances:
            self.labels[i] = KlippyGtk.ToggleButton(i)
            self.labels[i].connect("clicked", self.change_distance, i)
            ctx = self.labels[i].get_style_context()
            if j == 0:
                ctx.add_class("distbutton_top")
            elif j == len(self.distances)-1:
                ctx.add_class("distbutton_bottom")
            else:
                ctx.add_class("distbutton")
            if i == "1":
                ctx.add_class("distbutton_active")
            distgrid.attach(self.labels[i], j, 0, 1, 1)
            j += 1

        self.labels["1"].set_active(True)

        space_grid = KlippyGtk.HomogeneousGrid()
        space_grid.attach(Gtk.Label("Distance (mm):"),0,0,1,1)
        space_grid.attach(distgrid,0,1,1,1)
        space_grid.attach(Gtk.Label(" "),0,2,1,1)
        grid.attach(space_grid, 0, 2, 3, 1)



        b = KlippyGtk.ButtonImage('back', 'Back')
        b.connect("clicked", self._screen._menu_go_back)
        grid.attach(b, 3, 2, 1, 1)

        self.grid = grid

    def get(self):
        return self.grid

    def home(self, widget):
        self._screen._ws.send_method("post_printer_gcode", {"script": KlippyGcodes.HOME})

    def change_distance(self, widget, distance):
        if self.distance == distance:
            return
        print "### Distance " + str(distance)

        ctx = self.labels[str(self.distance)].get_style_context()
        ctx.remove_class("distbutton_active")

        self.distance = distance
        ctx = self.labels[self.distance].get_style_context()
        ctx.add_class("distbutton_active")
        for i in self.distances:
            if i == self.distance:
                continue
            self.labels[str(i)].set_active(False)

    def move(self, widget, axis, dir):
        dist = str(self.distance) if dir == "+" else "-" + str(self.distance)
        print "# Moving " + axis + " " + dist + "mm"


        self._screen._ws.send_method("post_printer_gcode_script", {"script": KlippyGcodes.MOVE_RELATIVE})
        self._screen._ws.send_method("post_printer_gcode_script", {"script": KlippyGcodes.MOVE + " "+axis+dist})
