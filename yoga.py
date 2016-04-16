#!/usr/bin/env python

import signal
import subprocess
import re

from PyQt4 import QtGui, QtCore

APPINDICATOR_ID = 'yoga-applet'
touch = ""
stylus = ""
eraser = ""
video_driver = ""

class Menu(QtGui.QMenu):
    def __init__(self, parent=None):
        QtGui.QMenu.__init__(self, "Yoga", parent)

        is_nvidia = (video_driver == 'nvidia')

        self.everything_menu = QtGui.QAction("&Everything", self)
        self.everything_menu.triggered.connect(self.enable_everything)

        self.addAction(self.everything_menu)

        self.touchpad_and_pen_menu = QtGui.QAction("&Touchpad and Pen", self)
        self.touchpad_and_pen_menu.triggered.connect(self.touchpad_and_pen)

        self.addAction(self.touchpad_and_pen_menu)
        self.addSeparator()

        self.tablet_everything_menu = QtGui.QAction("&Tablet - Everything", self)
        self.tablet_everything_menu.triggered.connect(self.tablet_everything)
        self.tablet_everything_menu.setDisabled(is_nvidia)

        self.addAction(self.tablet_everything_menu)

        self.tablet_pen_only_menu = QtGui.QAction("&Tablet - Pen Only", self)
        self.tablet_pen_only_menu.triggered.connect(self.tablet_pen_only)
        self.tablet_pen_only_menu.setDisabled(is_nvidia)

        self.addAction(self.tablet_pen_only_menu)

        self.righty_everything_menu = QtGui.QAction("&Righty - Everything", self)
        self.righty_everything_menu.triggered.connect(self.righty_everything)
        self.righty_everything_menu.setDisabled(is_nvidia)

        self.addAction(self.righty_everything_menu)

    def touchpad_and_pen(self, event):
        self.do_rotate('none')
        self.do_disable_touch()
        self.do_enable_trackpad()

    def enable_everything(self, event):
        self.do_rotate('none')
        self.do_enable_touch()
        self.do_enable_trackpad()

    def tablet_everything(self, event):
        self.do_rotate('half')
        self.do_enable_touch()
        self.do_disable_trackpad()

    def tablet_pen_only(self, event):
        self.do_rotate('half')
        self.do_disable_touch()
        self.do_disable_trackpad()

    def righty_everything(self, event):
        self.do_rotate('ccw')
        self.do_enable_touch()
        self.do_disable_trackpad()

    def do_enable_touch(self):
        global touch

        subprocess.call("xsetwacom --set '{}' gesture on".format(touch), shell=True)
        subprocess.call("xsetwacom --set '{}' touch on".format(touch), shell=True)

    def do_disable_touch(self):
        global touch

        subprocess.call("xsetwacom --set '{}' gesture off".format(touch), shell=True)
        subprocess.call("xsetwacom --set '{}' touch off".format(touch), shell=True)

    def do_enable_trackpad(self):
        global touchpad_id

        subprocess.call("xinput enable {}".format(touchpad_id), shell=True)

    def do_disable_trackpad(self):
        global touchpad_id

        subprocess.call("xinput disable {}".format(touchpad_id), shell=True)

    def do_rotate(self, direction):
        for device in [touch, stylus, eraser]:
            subprocess.call("xsetwacom --set '{}' rotate {}".format(device, direction), shell=True)

        xrandr_rotates = {
            "none": "normal",
            "half": "inverted",
            "ccw": "left",
        }

        subprocess.call("xrandr -o {}".format(xrandr_rotates[direction]), shell=True)

class SystemTrayIcon(QtGui.QSystemTrayIcon):
    def __init__(self, parent=None):
        QtGui.QSystemTrayIcon.__init__(self, parent)
        self.setIcon(QtGui.QIcon.fromTheme('document-save'))

        self.left_menu = Menu()
        self.activated.connect(self.click_trap)

    def click_trap(self, value):
        if value == self.Trigger:
            self.left_menu.exec_(QtGui.QCursor.pos())

    def show(self):
        QtGui.QSystemTrayIcon.show(self)

def main():
    global touch, stylus, eraser, video_driver, touchpad_id

    devices = subprocess.check_output('xsetwacom --list devices', shell=True).split('\n')
    for x in devices:
        if 'type: TOUCH' in x:
            touch = x.split('\t')[0]
        if 'type: STYLUS' in x:
            stylus = x.split('\t')[0]
        if 'type: ERASER' in x:
            eraser = x.split('\t')[0]

    devices = subprocess.check_output('xinput list', shell=True).split('\n')
    for x in devices:
        if 'Touchpad' in x:
            result = re.search('id=(\d+)', x)
            touchpad_id = result.group(1)

    print touchpad_id

    video_driver = subprocess.check_output('prime-select query', shell=True).split('\n')[0]

    print video_driver

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QtGui.QApplication([])

    icon = SystemTrayIcon()
    icon.show()

    app.exec_()

def click_indicator():
    print "hi"

if __name__ == "__main__":
    main()
