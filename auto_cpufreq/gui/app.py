import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GLib

import sys
import os

sys.path.append("../../")
from auto_cpufreq.core import sysinfo, distro_info, getoutput, set_override

from io import StringIO

HBOX_PADDING = 20

class RadioButtonView(Gtk.Box):
    def __init__(self):
        super().__init__()
        self.set_valign(Gtk.Align.START)

        default = Gtk.RadioButton.new_with_label_from_widget(None, "Default")
        default.connect("toggled", self.on_button_toggled,  "reset")
        powersave = Gtk.RadioButton.new_with_label_from_widget(default, "Powersave")
        powersave.connect("toggled", self.on_button_toggled,  "powersave")
        performance = Gtk.RadioButton.new_with_label_from_widget(default, "Performance")
        performance.connect("toggled", self.on_button_toggled, "performance")
        
        self.pack_start(default, False, False, 0)
        self.pack_start(powersave, False, False, 0)
        self.pack_start(performance, False, False, 0)

    def on_button_toggled(self, button, override):
        if button.get_active():
            set_override(override)


class CurrentGovernorBox(Gtk.Box):
    def __init__(self):
        super().__init__(spacing=60)

        self.static = Gtk.Label(label="Current Governor")
        self.governor = Gtk.Label(label=getoutput("cpufreqctl.auto-cpufreq --governor").strip().split(" ")[0])

        self.pack_start(self.static, False, False, 0)
        self.pack_start(self.governor, False, False, 0)

    def refresh(self):
        self.governor.set_label(getoutput("cpufreqctl.auto-cpufreq --governor").strip().split(" ")[0])

class SystemStatsLabel(Gtk.Label):
    def __init__(self):
        super().__init__()

        self.update()

    def update(self):
        # change stdout and store label text to file-like object
        old_stdout = sys.stdout
        text = StringIO()
        sys.stdout = text
        sysinfo()
        distro_info()
        self.set_label(text.getvalue())
        sys.stdout = old_stdout
        
    def refresh(self):
        self.update()

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