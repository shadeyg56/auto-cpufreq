from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import os

CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

app = QApplication([])
app.setQuitOnLastWindowClosed(False)

icon = QIcon(os.path.join(CURRENT_DIRECTORY, "icon.png"))

tray = QSystemTrayIcon(icon, app)
tray.setIcon(icon)
tray.setVisible(True)
print(tray.icon().name())
print(icon.State)
print(os.path.join(CURRENT_DIRECTORY, "reddit-logo.png"))

menu = QMenu()
option1 = QAction("Test")
option2 = QAction("Hello World")
menu.addAction(option1)
menu.addAction(option2)

quit = QAction("Quit")
quit.triggered.connect(app.quit)
menu.addAction(quit)

tray.setContextMenu(menu)

app.exec_()