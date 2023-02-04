import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GLib

import os

from objects import RadioButtonView, SystemStatsLabel, CPUFreqStatsLabel, CurrentGovernorBox

HBOX_PADDING = 20

class MyWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="auto-cpufreq")
        self.set_default_size(640, 480)
        self.set_border_width(10)

        settings = Gtk.Settings.get_default()
        # Theme
        theme = os.environ.get("GTK_THEME")
        if theme is not None:
            settings.set_property("gtk-theme-name", theme)

        # main HBOX
        self.hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=HBOX_PADDING)
        self.add(self.hbox)
       
        self.systemstats = SystemStatsLabel()
        self.hbox.pack_start(self.systemstats, False, False, 0)

        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.currentgovernor = CurrentGovernorBox()
        self.vbox.pack_start(self.currentgovernor, False, False, 0)
        self.vbox.pack_start(RadioButtonView(), False, False, 0)

        self.cpufreqstats = CPUFreqStatsLabel()
        self.vbox.pack_start(self.cpufreqstats, False, False, 0)

        self.hbox.pack_start(self.vbox, False, False, 0)

        GLib.timeout_add_seconds(2, self.refresh)

    def refresh(self):
        self.systemstats.refresh()
        self.currentgovernor.refresh()

        return True



win = MyWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()