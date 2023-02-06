import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, GdkPixbuf

import sys
import os

sys.path.append("../../")
from subprocess import getoutput
from auto_cpufreq.core import sysinfo, distro_info, set_override, get_override

from io import StringIO

if os.getenv("PKG_MARKER") == "SNAP":
    auto_cpufreq_stats_path = "/var/snap/auto-cpufreq/current/auto-cpufreq.stats"
else:
    auto_cpufreq_stats_path = "/var/run/auto-cpufreq.stats"


def get_stats():
    if os.path.isfile(auto_cpufreq_stats_path):
        with open(auto_cpufreq_stats_path, "r") as file:
            stats = [line for line in (file.readlines() [-50:])]
        return "".join(stats)


class RadioButtonView(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.set_valign(Gtk.Align.START)

        self.hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        self.label = Gtk.Label("Governor Override")

        self.default = Gtk.RadioButton.new_with_label_from_widget(None, "Default")
        self.default.connect("toggled", self.on_button_toggled,  "reset")
        self.powersave = Gtk.RadioButton.new_with_label_from_widget(self.default, "Powersave")
        self.powersave.connect("toggled", self.on_button_toggled,  "powersave")
        self.performance = Gtk.RadioButton.new_with_label_from_widget(self.default, "Performance")
        self.performance.connect("toggled", self.on_button_toggled, "performance")
        
        self.set_selected()

        self.hbox.pack_start(self.default, False, False, 0)
        self.hbox.pack_start(self.powersave, False, False, 0)
        self.hbox.pack_start(self.performance, False, False, 0)

        self.pack_start(self.label, False, False, 0)
        self.pack_start(self.hbox, False, False, 0)

    def on_button_toggled(self, button, override):
        if button.get_active():
            set_override(override)

    def set_selected(self):
        override = get_override()
        match override:
            case "powersave":
                self.powersave.set_active(True)
            case "performance":
                self.performance.set_active(True)
            case "default":
                self.default.set_active(True)

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

class CPUFreqStatsLabel(Gtk.Label):
    def __init__(self):
        super().__init__()

        self.update()
  
    def update(self):
        stats = get_stats().split("\n")
        start = None
        for i, line in enumerate(stats):
            if line == ("-" * 28 + " CPU frequency scaling " + "-" * 28):
                start = i
                break
        if start is not None:
            del stats[:i]
            del stats[-4:]
            self.set_label("\n".join(stats))
 
class DropDownMenu(Gtk.MenuButton):
    def __init__(self, parent):
        super().__init__()
        self.set_halign(Gtk.Align.END)
        img_buffer = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                    filename="/usr/local/share/auto-cpufreq/images/menu.png",
                    width=25,
                    height=25,
                    preserve_aspect_ratio=True)
        self.image = Gtk.Image.new_from_pixbuf(img_buffer)
        self.add(self.image)
        self.menu = self.build_menu(parent)
        self.set_popup(self.menu)

    def build_menu(self, parent):
        menu = Gtk.Menu()

        daemon = Gtk.MenuItem(label="Remove Daemon")
        menu.append(daemon)

        about = Gtk.MenuItem(label="About")
        about.connect("activate", self.about_dialog, parent)
        menu.append(about)

        menu.show_all()
        return menu

    def about_dialog(self, MenuItem, parent):
        dialog = AboutDialog(parent)
        response = dialog.run()
        dialog.destroy()


class AboutDialog(Gtk.Dialog):
    def __init__(self, parent):
        super().__init__(title="About", transient_for=parent)
        self.box = self.get_content_area()
        self.add_button("Close", Gtk.ResponseType.CLOSE)
        self.set_default_size(150, 100)

        label = Gtk.Label("Hello World")
        self.box.pack_start(label, False, False, 0)
        self.show_all()