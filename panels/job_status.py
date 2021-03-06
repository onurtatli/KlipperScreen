# -*- coding: utf-8 -*-
import gi
import logging
import math

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib, Pango

from ks_includes.screen_panel import ScreenPanel

logger = logging.getLogger("KlipperScreen.JobStatusPanel")

def create_panel(*args):
    return JobStatusPanel(*args)

class JobStatusPanel(ScreenPanel):
    is_paused = False
    filename = None
    file_metadata = {}
    progress = 0
    state = "printing"

    def initialize(self, panel_name):
        _ = self.lang.gettext
        self.layout = Gtk.Layout()
        self.layout.set_size(self._screen.width, self._screen.height)
        self.timeleft_type = "file"

        self.create_buttons()

        grid = self._gtk.HomogeneousGrid()
        grid.set_size_request(self._screen.width, self._screen.height)

        fi_box = Gtk.VBox(spacing=0)
        fi_box.set_hexpand(True)
        fi_box.set_vexpand(False)
        fi_box.set_halign(Gtk.Align.START)

        self.labels['file'] = Gtk.Label(label="file")
        self.labels['file'].set_halign(Gtk.Align.START)
        self.labels['file'].set_vexpand(False)
        self.labels['file'].get_style_context().add_class("printing-filename")
        self.labels['file'].set_line_wrap(True)
        self.labels['file'].set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        self.labels['status'] = Gtk.Label()
        self.labels['status'].set_halign(Gtk.Align.START)
        self.labels['status'].set_vexpand(False)
        self.labels['status'].get_style_context().add_class("printing-status")

        fi_box.add(self.labels['file']) #, True, True, 0)
        fi_box.add(self.labels['status']) #, True, True, 0)
        fi_box.set_valign(Gtk.Align.CENTER)

        info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        info.props.valign = Gtk.Align.CENTER
        info.set_hexpand(True)
        info.set_vexpand(True)
        #info.add(self.labels['file']['b'])
        #info.add(self.labels['time']['b'])
        #info.add(self.labels['time_left']['b'])

        #grid.attach(info,2,0,2,1)

        #pbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        #pbox.pack_start(self.labels['file']['b'], False, True, 0)
        #pbox.pack_end(timegrid, False, False, 0)
        #pbox.pack_end(self.labels['progress'], False, False, 0)
        #pbox.pack_end(overlay, False, False, 0)

        #grid.attach(pbox, 0, 0, 4, 3)
        self.labels['darea'] = Gtk.DrawingArea()
        self.labels['darea'].connect("draw", self.on_draw)

        box = Gtk.Box()
        box.set_hexpand(True)
        box.set_vexpand(True)
        box.set_halign(Gtk.Align.CENTER)
        self.labels['progress_text'] = Gtk.Label()
        self.labels['progress_text'].get_style_context().add_class("printing-progress-text")
        box.add(self.labels['progress_text'])

        overlay = Gtk.Overlay()
        overlay.set_hexpand(True)
        overlay.set_vexpand(True)
        overlay.add(self.labels['darea'])
        overlay.add_overlay(box)

        #self.labels['extruder'] = self._gtk.ButtonImage("extruder-1", self._gtk.formatTemperatureString(0, 0))
        #self.labels['extruder'].set_sensitive(False)
        #grid.attach(self.labels['extruder'], 0, 0, 1, 1)

        #self.labels['heater_bed'] = self._gtk.ButtonImage("bed", self._gtk.formatTemperatureString(0, 0))
        #self.labels['heater_bed'].set_sensitive(False)
        #grid.attach(self.labels['heater_bed'], 0, 1, 1, 1)

        self.labels['thumbnail'] = self._gtk.Image("file.svg", False, 1.6, 1.6)

        i = 0
        for extruder in self._printer.get_tools():
            self.labels[extruder + '_box'] = Gtk.Box(spacing=0)
            self.labels[extruder] = Gtk.Label(label="")
            self.labels[extruder].get_style_context().add_class("printing-info")
            if i <= 4:
                ext_img = self._gtk.Image("extruder-%s.svg" % i, None, .6, .6)
                self.labels[extruder + '_box'].add(ext_img)
            self.labels[extruder + '_box'].add(self.labels[extruder])
            i += 1

        temp_grid = self._gtk.HomogeneousGrid()
        self.current_extruder = self._printer.get_stat("toolhead","extruder")
        temp_grid.attach(self.labels[self.current_extruder + '_box'], 0, 0, 1, 1)
        if self._printer.has_heated_bed():
            heater_bed = self._gtk.Image("bed.svg", None, .6, .6)
            self.labels['heater_bed'] = Gtk.Label(label="")
            self.labels['heater_bed'].get_style_context().add_class("printing-info")
            heater_bed_box = Gtk.Box(spacing=0)
            heater_bed_box.add(heater_bed)
            heater_bed_box.add(self.labels['heater_bed'])
            temp_grid.attach(heater_bed_box, 1, 0, 1, 1)
        self.labels['temp_grid'] = temp_grid

        # Create time remaining items
        hourglass = self._gtk.Image("hourglass.svg", None, .6, .6)
        self.labels['left'] = Gtk.Label(label=_("Left:"))
        self.labels['left'].get_style_context().add_class("printing-info")
        self.labels['time_left'] = Gtk.Label(label="0s")
        self.labels['time_left'].get_style_context().add_class("printing-info")
        itl_box = Gtk.Box(spacing=0)
        itl_box.add(hourglass)
        itl_box.add(self.labels['left'])
        itl_box.add(self.labels['time_left'])
        self.labels['itl_box'] = itl_box

        # Create overall items
        clock = self._gtk.Image("clock.svg", None, .6, .6)
        self.labels['elapsed'] = Gtk.Label(label=_("Elapsed:"))
        self.labels['elapsed'].get_style_context().add_class("printing-info")
        self.labels['duration'] = Gtk.Label(label="0s")
        self.labels['duration'].get_style_context().add_class("printing-info")
        self.labels['est_time'] = Gtk.Label(label="/ 0s")
        self.labels['est_time'].get_style_context().add_class("printing-info")
        it_box = Gtk.Box(spacing=0)
        it_box.add(clock)
        it_box.add(self.labels['elapsed'])
        it_box.add(self.labels['duration'])
        it_box.add(self.labels['est_time'])
        self.labels['it_box'] = it_box

        position = self._gtk.Image("move.svg", None, .6, .6)
        self.labels['pos_x'] = Gtk.Label(label="X: 0")
        self.labels['pos_x'].get_style_context().add_class("printing-info")
        self.labels['pos_y'] = Gtk.Label(label="Y: 0")
        self.labels['pos_y'].get_style_context().add_class("printing-info")
        self.labels['pos_z'] = Gtk.Label(label="Z: 0")
        self.labels['pos_z'].get_style_context().add_class("printing-info")
        pos_box = Gtk.Box(spacing=0)
        posgrid = self._gtk.HomogeneousGrid()
        posgrid.set_hexpand(True)
        posgrid.attach(self.labels['pos_x'], 0, 0, 1, 1)
        posgrid.attach(self.labels['pos_y'], 1, 0, 1, 1)
        posgrid.attach(self.labels['pos_z'], 2, 0, 1, 1)
        pos_box.add(position)
        pos_box.add(posgrid)
        self.labels['pos_box'] = pos_box

        speed = self._gtk.Image("speed-step.svg", None, .6, .6)
        self.labels['speed'] = Gtk.Label(label="")
        self.labels['speed'].get_style_context().add_class("printing-info")
        speed_box = Gtk.Box(spacing=0)
        speed_box.add(speed)
        speed_box.add(self.labels['speed'])
        extrusion = self._gtk.Image("extrude.svg", None, .6, .6)
        self.labels['extrusion'] = Gtk.Label(label="")
        self.labels['extrusion'].get_style_context().add_class("printing-info")
        extrusion_box = Gtk.Box(spacing=0)
        extrusion_box.add(extrusion)
        extrusion_box.add(self.labels['extrusion'])
        fan = self._gtk.Image("fan.svg", None, .6, .6)
        self.labels['fan'] = Gtk.Label(label="")
        self.labels['fan'].get_style_context().add_class("printing-info")
        fan_box = Gtk.Box(spacing=0)
        fan_box.add(fan)
        fan_box.add(self.labels['fan'])
        sfe_grid = self._gtk.HomogeneousGrid()
        sfe_grid.set_hexpand(True)
        sfe_grid.attach(speed_box, 0, 0, 1, 1)
        sfe_grid.attach(extrusion_box, 1, 0, 1, 1)
        sfe_grid.attach(fan_box, 2, 0, 1, 1)
        self.labels['sfe_grid'] = sfe_grid

        self.labels['i1_box'] = Gtk.VBox(spacing=0)
        self.labels['i1_box'].get_style_context().add_class("printing-info-box")
        self.labels['i1_box'].set_valign(Gtk.Align.CENTER)
        self.labels['i2_box'] = Gtk.VBox(spacing=0)
        self.labels['i2_box'].get_style_context().add_class("printing-info-box")

        grid.attach(overlay, 0, 0, 1, 1)
        grid.attach(fi_box, 1, 0, 3, 1)
        grid.attach(self.labels['i1_box'], 0, 1, 2, 2)
        grid.attach(self.labels['i2_box'], 2, 1, 2, 2)

        self.add_labels()

        self.grid = grid
        self.layout.put(grid, 0, 0)

        self._screen.add_subscription(panel_name)

    def on_draw(self, da, ctx):
        w = da.get_allocated_width()
        h = da.get_allocated_height()
        r = min(w,h)*.4

        ctx.set_source_rgb(0.6, 0.6, 0.6)
        ctx.set_line_width(self._gtk.get_font_size() * .75)
        ctx.translate(w / 2, h / 2)
        ctx.arc(0, 0, r, 0, 2*math.pi)
        ctx.stroke()

        ctx.set_source_rgb(1, 0, 0)
        ctx.arc(0, 0, r, 3/2*math.pi, 3/2*math.pi+(self.progress*2*math.pi))
        ctx.stroke()


    def activate(self):
        _ = self.lang.gettext
        self.progress = self._printer.get_stat('virtual_sdcard','progress')
        self.update_progress()
        self.enable_button("pause","cancel","resume")

        state = "printing"
        self.update_text("status",_("Printing"))

        self.filename = self._printer.get_stat('print_stats','filename')
        self.update_file_metadata()

        self.grid.remove_row(3)
        self.grid.insert_row(3)

        ps = self._printer.get_stat("print_stats")
        logger.debug("Act State: %s" % ps['state'])
        self.set_state(ps['state'])
        self.show_buttons_for_state()

    def add_labels(self):
        for child in self.labels['i1_box'].get_children():
            self.labels['i1_box'].remove(child)
        for child in self.labels['i2_box'].get_children():
            self.labels['i2_box'].remove(child)

        #if self.file_metadata == None:
        #    self.labels['i1_box'].add(self.labels['temp_grid'])
        #    self.labels['i1_box'].add(self.labels['pos_box'])
        #    self.labels['i1_box'].add(self.labels['sfe_grid'])
        #    self.labels['i2_box'].add(self.labels['it_box'])
        #    self.labels['i2_box'].add(self.labels['itl_box'])
        #else:
        self.labels['i1_box'].add(self.labels['thumbnail'])
        self.labels['i2_box'].add(self.labels['temp_grid'])
        self.labels['i2_box'].add(self.labels['pos_box'])
        self.labels['i2_box'].add(self.labels['sfe_grid'])
        self.labels['i2_box'].add(self.labels['it_box'])
        self.labels['i2_box'].add(self.labels['itl_box'])


    def create_buttons(self):
        _ = self.lang.gettext
        self.labels['cancel'] = self._gtk.ButtonImage("stop",_("Cancel"),"color2")
        self.labels['cancel'].connect("clicked", self.cancel)
        self.labels['control'] = self._gtk.ButtonImage("control",_("Control"),"color3")
        self.labels['control'].connect("clicked", self._screen._go_to_submenu, "")
        self.labels['estop'] = self._gtk.ButtonImage("emergency",_("Emergency Stop"),"color4")
        self.labels['estop'].connect("clicked", self.emergency_stop)
        self.labels['menu'] = self._gtk.ButtonImage("complete",_("Main Menu"),"color4")
        self.labels['menu'].connect("clicked", self.close_panel)
        self.labels['pause'] = self._gtk.ButtonImage("pause",_("Pause"),"color1" )
        self.labels['pause'].connect("clicked",self.pause)
        self.labels['restart'] = self._gtk.ButtonImage("restart",_("Restart"),"color3")
        self.labels['restart'].connect("clicked", self.restart)
        self.labels['resume'] = self._gtk.ButtonImage("resume",_("Resume"),"color1")
        self.labels['resume'].connect("clicked",self.resume)

    def restart(self, widget):
        if self.filename != "none":
            self._screen._ws.klippy.print_start(self.filename)

    def resume(self, widget):
        #self.disable_button("resume","cancel")
        self._screen._ws.klippy.print_resume(self._response_callback, "enable_button", "pause", "cancel")
        self._screen.show_all()

    def pause(self, widget):
        #self.disable_button("pause","cancel")
        self._screen._ws.klippy.print_pause(self._response_callback, "enable_button", "resume", "cancel")
        self._screen.show_all()

    def cancel(self, widget):
        _ = self.lang.gettext

        buttons = [
            {"name": _("Cancel Print"), "response": Gtk.ResponseType.OK},
            {"name": _("Go Back"), "response": Gtk.ResponseType.CANCEL}
        ]

        label = Gtk.Label()
        label.set_markup(_("Are you sure you wish to cancel this print?"))
        label.set_hexpand(True)
        label.set_halign(Gtk.Align.CENTER)
        label.set_line_wrap(True)
        label.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)

        dialog = self._gtk.Dialog(self._screen, buttons, label, self.cancel_confirm)
        self.disable_button("pause","cancel")

    def cancel_confirm(self, widget, response_id):
        widget.destroy()

        if response_id == Gtk.ResponseType.CANCEL:
            self.enable_button("pause","cancel")
            return

        logger.debug("Canceling print")
        self.disable_button("pause","resume","cancel")
        self._screen._ws.klippy.print_cancel(self._response_callback)

    def _response_callback(self, response, method, params, func=None, *args):
        if func == "enable_button":
            self.enable_button(*args)

    def close_panel(self, widget=None):
        if self._screen.is_printing():
            self._screen.printer_ready()
        return False

    def enable_button(self, *args):
        for arg in args:
            self.labels[arg].set_sensitive(True)

    def disable_button(self, *args):
        for arg in args:
            self.labels[arg].set_sensitive(False)

    def _callback_metadata(self, newfiles, deletedfiles, modifiedfiles):
        if self.file_metadata == None and self.filename in modifiedfiles:
            self.update_file_metadata()
            self._files.remove_file_callback(self._callback_metadata)

    def process_update(self, action, data):
        if action != "notify_status_update":
            return
        _ = self.lang.gettext

        if self._printer.has_heated_bed():
            self.update_temp("heater_bed",
                self._printer.get_dev_stat("heater_bed","temperature"),
                self._printer.get_dev_stat("heater_bed","target")
            )
        for x in self._printer.get_tools():
            self.update_temp(x,
                self._printer.get_dev_stat(x,"temperature"),
                self._printer.get_dev_stat(x,"target")
            )


        if "toolhead" in data:
            if "extruder" in data["toolhead"]:
                if data["toolhead"]["extruder"] != self.current_extruder:
                    self.labels['temp_grid'].remove_column(0)
                    self.labels['temp_grid'].insert_column(0)
                    self.current_extruder = data["toolhead"]["extruder"]
                    self.labels['temp_grid'].attach(self.labels[self.current_extruder + '_box'], 0, 0, 1, 1)
                    self._screen.show_all()
            if "position" in data["toolhead"]:
                self.labels['pos_x'].set_text("X: %.2f" % (data["toolhead"]["position"][0]))
                self.labels['pos_y'].set_text("Y: %.2f" % (data["toolhead"]["position"][1]))
        if "gcode_move" in data and "gcode_position" in data["gcode_move"]:
            self.labels['pos_z'].set_text("Z: %.2f" % (data["gcode_move"]["gcode_position"][2]))

        if "gcode_move" in data:
            #if "homing_origin" in data["gcode_move"]:
            #    self.labels['zoffset'].set_text("%.2fmm" % data["gcode_move"]["homing_origin"][2])
            if "extrude_factor" in data["gcode_move"]:
                self.extrusion = int(data["gcode_move"]["extrude_factor"]*100)
                self.labels['extrusion'].set_text("%3d%%" % self.extrusion)
            if "speed_factor" in data["gcode_move"]:
                self.speed = int(data["gcode_move"]["speed_factor"]*100)
                self.labels['speed'].set_text("%3d%%" % self.speed)
        if "fan" in data and "speed" in data['fan']:
            self.fan = int(round(data['fan']['speed'],2)*100)
            self.labels['fan'].set_text("%3d%%" % self.fan)

        if "print_stats" in data or "virtual_sdcard" in data:
            ps = self._printer.get_stat("print_stats")
            vsd = self._printer.get_stat("virtual_sdcard")
            if ps['state'] == "printing" and self.state != "printing":
                self.set_state("printing")
                self.show_buttons_for_state()
            if ps['state'] == "complete" and self.state != "complete":
                self.progress = 1
                self.update_progress()
                self.set_state("complete")
                self.show_buttons_for_state()
                timeout = self._config.get_main_config().getint("job_complete_timeout", 30)
                if timeout != 0:
                    GLib.timeout_add(timeout * 1000, self.close_panel)
            elif ps['state'] == "error" and self.state != "error":
                logger.debug("Error!")
                self.set_state("error")
                self.labels['status'].set_text("Error - %s" % ps['message'])
                self.show_buttons_for_state()
                timeout = self._config.get_main_config().getint("job_error_timeout", 0)
                if timeout != 0:
                    GLib.timeout_add(timeout * 1000, self.close_panel)
            elif ps['state'] == "standby":
                self.close_panel()

            if self.filename != ps['filename']:
                if ps['filename'] != "":
                    self.filename = ps['filename']
                    self.file_metadata = {}
                    self.update_text("file", self.filename.split("/")[-1])
                else:
                    file = "Unknown"
                    self.update_text("file", "Unknown file")

            if self.file_metadata != None:
                if "gcode_start_byte" in self.file_metadata:
                    progress = (max(vsd['file_position'] - self.file_metadata['gcode_start_byte'],0) /
                        (self.file_metadata['gcode_end_byte'] - self.file_metadata['gcode_start_byte']))
                else:
                    progress = 0 if self._printer.get_stat('virtual_sdcard','progress') == 0 else (ps['print_duration']/
                        self._printer.get_stat('virtual_sdcard','progress') - ps['print_duration'])
                progress = round(progress,2)

                if progress != self.progress:
                    self.progress = progress
                    self.labels['darea'].queue_draw()

                self.update_text("duration", str(self._gtk.formatTimeString(ps['print_duration'])))

            timeleft_type = self._config.get_config()['main'].get('print_estimate_method','file')

            if timeleft_type != self.timeleft_type:
                if self.timeleft_type == "duration":
                    self.labels['it_box'].add(self.labels['est_time'])
                elif timeleft_type == "duration":
                    self.labels['it_box'].remove(self.labels['est_time'])
                self.timeleft_type = timeleft_type

            if timeleft_type in ['filament','file','slicer']:
                duration = ps['print_duration']
                if timeleft_type == "filament":
                    estimated_filament = (self.file_metadata['filament_total'] if "filament_total" in self.file_metadata
                            else 1)
                    total_duration = duration / (ps['filament_used'] / estimated_filament)
                elif timeleft_type == "file":
                    total_duration = duration / max(self.progress, 0.0001)
                elif timeleft_type == "slicer":
                    total_duration = (self.file_metadata['estimated_time'] if "estimated_time" in self.file_metadata
                            else duration)

                time_left = max(total_duration - duration, 0)
                self.update_text("time_left", str(self._gtk.formatTimeString(time_left)))

            self.update_progress()

        if "pause_resume" in data and self.state != "complete":
            if self.state == "paused" and data['pause_resume']['is_paused'] == False:
                self.set_state("printing")
                self.update_text("status",_("Paused"))
                self.grid.attach(self.labels['pause'], 0, 3, 1, 1)
                self.grid.remove(self.labels['resume'])
                self.grid.show_all()
            if self.state != "paused" and data['pause_resume']['is_paused'] == True:
                self.set_state("paused")
                self.grid.attach(self.labels['resume'], 0, 3, 1, 1)
                self.grid.remove(self.labels['pause'])
                self.grid.show_all()

    def set_state(self, state):
        self.state = state
        self.update_text("status",state.capitalize())

    def show_buttons_for_state(self):
        self.grid.remove_row(3)
        self.grid.insert_row(3)
        if self.state == "printing":
            self.grid.attach(self.labels['pause'], 0, 3, 1, 1)
            self.grid.attach(self.labels['cancel'], 1, 3, 1, 1)
            self.grid.attach(self.labels['estop'], 2, 3, 1, 1)
            self.grid.attach(self.labels['control'], 3, 3, 1, 1)
        elif self.state == "paused":
            self.grid.attach(self.labels['resume'], 0, 3, 1, 1)
            self.grid.attach(self.labels['cancel'], 1, 3, 1, 1)
            self.grid.attach(self.labels['estop'], 2, 3, 1, 1)
            self.grid.attach(self.labels['control'], 3, 3, 1, 1)
        elif self.state == "error" or self.state == "complete":
            self.grid.attach(self.labels['restart'], 2, 3, 1, 1)
            self.grid.attach(self.labels['menu'], 3, 3, 1, 1)
        self.show_all()

    def show_file_thumbnail(self):
        if self._files.has_thumbnail(self.filename):
            pixbuf = self.get_file_image(self.filename, 7, 3.25)
            if pixbuf != None:
                self.labels['thumbnail'].set_from_pixbuf(pixbuf)

    def update_file_metadata(self):
        if self._files.file_metadata_exists(self.filename):
            self.file_metadata = self._files.get_file_info(self.filename)
            logger.debug("Parsing file metadata: %s" % list(self.file_metadata))
            self.update_text("est_time","/ %s" % str(self._gtk.formatTimeString(self.file_metadata['estimated_time'])))
            if "thumbnails" in self.file_metadata:
                tmp = self.file_metadata['thumbnails'].copy()
                for i in tmp:
                    i['data'] = ""
                logger.debug("Thumbnails: %s" % list(tmp))
            self.show_file_thumbnail()
        else:
            self.file_metadata = None
            logger.debug("Cannot find file metadata. Listening for updated metadata")
            self._screen.files.add_file_callback(self._callback_metadata)

    def update_image_text(self, label, text):
        if label in self.labels and 'l' in self.labels[label]:
            self.labels[label]['l'].set_text(text)

    def update_text(self, label, text):
        if label in self.labels:
            self.labels[label].set_text(text)

    def update_progress (self):
        self.labels['progress_text'].set_text("%s%%" % (str( min(int(self.progress*100),100) )))

    #def update_temp(self, dev, temp, target):
    #    if dev in self.labels:
    #        self.labels[dev].set_label(self._gtk.formatTemperatureString(temp, target))

    def update_temp(self, x, temp, target):
        self.labels[x].set_markup(
            "%.1f<big>/</big>%.0f °C" % (temp, target)
        )
