import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

from KlippyGtk import KlippyGtk
from KlippyGcodes import KlippyGcodes

class TemperaturePanel:
    _screen = None
    labels = {}
    active_heater = "tool0"

    def __init__(self, screen):
        self._screen = screen


    def initialize(self):

        grid = KlippyGtk.HomogeneousGrid()

        eq_grid = KlippyGtk.HomogeneousGrid()
        for i in range(self._screen.extrudercount):
            if i > 3:
                break
            self.labels["tool" + str(i)] = KlippyGtk.ToggleButtonImage("extruder-"+str(i+1), KlippyGtk.formatTemperatureString(0, 0))
            self.labels["tool" + str(i)].connect('clicked', self.select_heater, "tool"+str(i))
            if i == 1:
                self.labels["tool0"].set_active(True)
            eq_grid.attach(self.labels["tool" + str(i)], i%2, i/2, 1, 1)

        ctx = self.labels["tool0"].get_style_context()
        ctx.add_class('button_active')

        self.labels['bed'] = KlippyGtk.ToggleButtonImage("bed", KlippyGtk.formatTemperatureString(0, 0))
        self.labels["bed"].connect('clicked', self.select_heater, "bed")
        width = 2 if i > 0 else 1
        eq_grid.attach(self.labels['bed'], 0, i/2+1, width, 1)


        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        self.labels['entry'] = Gtk.Entry()
        self.labels['entry'].props.xalign = 0.5
        ctx = self.labels['entry'].get_style_context()
        ctx.add_class('temperature_entry')

        numpad = KlippyGtk.HomogeneousGrid()

        keys = [
            ['1','numpad_tleft'],
            ['2','numpad_top'],
            ['3','numpad_tright'],
            ['4','numpad_left'],
            ['5','numpad_button'],
            ['6','numpad_right'],
            ['7','numpad_left'],
            ['8','numpad_button'],
            ['9','numpad_right'],
            ['B','numpad_bleft'],
            ['0','numpad_bottom'],
            ['E','numpad_bright']
        ]
        for i in range(len(keys)):
            id = 'button_' + str(keys[i][0])
            self.labels[id] = Gtk.Button(keys[i][0])
            self.labels[id].connect('clicked', self.update_entry, keys[i][0])
            ctx=self.labels[id].get_style_context()
            ctx.add_class(keys[i][1])
            numpad.attach(self.labels[id], i%3, i/3, 1, 1)

        numpad.attach(Gtk.Button("test"),0,0,1,1)

        box.add(self.labels['entry'])
        box.pack_end(numpad, True, True, 5)


        grid.attach(eq_grid, 0, 0, 1, 4)
        grid.attach(box, 1, 0, 1, 3)

        b = KlippyGtk.ButtonImage('back', 'Back')
        b.connect("clicked", self._screen._menu_go_back)
        grid.attach(b, 1, 3, 1, 1)

        self.grid = grid

        self.update_temp("bed",35,40)

    def get(self):
        # Return gtk item
        return self.grid

    def select_heater (self, widget, heater):
        if self.active_heater == heater:
            return

        ctx = self.labels[self.active_heater].get_style_context()
        ctx.remove_class('button_active')

        self.active_heater = heater
        ctx = self.labels[heater].get_style_context()
        ctx.add_class("button_active")
        self.labels['entry'].set_text("")

    def update_temp(self, dev, temp, target):
        if self.labels.has_key(dev):
            self.labels[dev].set_label(KlippyGtk.formatTemperatureString(temp, target))

    def update_entry(self, widget, digit):
        text = self.labels['entry'].get_text()
        if digit == 'B':
            if len(text) < 1:
                return
            self.labels['entry'].set_text(text[0:-1])
        elif digit == 'E':
            if self.active_heater == "bed":
                temp = int(self.labels['entry'].get_text())
                temp = 0 if temp < 0 or temp > KlippyGcodes.MAX_BED_TEMP else temp
                self._screen._ws.send_method("post_printer_gcode_script", {"script": KlippyGcodes.set_bed_temp(temp)})
            else:
                temp = int(self.labels['entry'].get_text())
                temp = 0 if temp < 0 or temp > KlippyGcodes.MAX_EXT_TEMP else temp
                print  KlippyGcodes.set_ext_temp(temp, self.active_heater.replace("tool",""))
                self._screen._ws.send_method("post_printer_gcode_script", {"script": KlippyGcodes.set_ext_temp(temp, self.active_heater.replace("tool",""))})
        else:
            if len(text) >= 3:
                return
            self.labels['entry'].set_text(text + digit)
