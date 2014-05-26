#!/usr/bin/env python

# This file is part of the Finna Pomodoro Project
# Copyright (C) 2014 Vinícius dos Santos Oliveira <vini.ipsmaker@gmail.com>
#
# This software is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any
# later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library.  If not, see <http://www.gnu.org/licenses/>.

import os
import dbus
import dbus.mainloop.glib
from gi.repository import Notify, GObject, Gtk, GLib
from datetime import datetime

ICON_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'icon.svg'))

Notify.init("PyPomodoro")

resumed_msg = Notify.Notification.new("Pomodoro resumed", 'Pomodoro', ICON_PATH)
paused_msg = Notify.Notification.new("Pomodoro paused", 'Pomodoro', ICON_PATH)
work_msg = Notify.Notification.new("Time to work", 'Pomodoro', ICON_PATH)
procrastinate_msg = Notify.Notification.new("Time to procrastinate", 'Pomodoro',
                                            ICON_PATH)

mainloop = GObject.MainLoop()

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

bus = dbus.SessionBus()
bus_name = 'io.github.finna_pomodoro_project' #< The service name
object_path = '/io/github/finna_pomodoro_project/Pomodoro'
dbus_interface = 'io.github.finna_pomodoro_project.Pomodoro'

# The user's voice

class PomodoroWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="PyPomodoro")

        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(self.vbox)

        self.label = Gtk.Label("Pomodoro")
        self.vbox.pack_start(self.label, True, True, 0)

        self.toggle_button = Gtk.Button(label="Toggle")
        self.toggle_button.connect("clicked", self.on_toggle_button_clicked)
        self.vbox.pack_start(self.toggle_button, True, True, 0)

        self.hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.vbox.pack_start(self.hbox, True, True, 0)

        self.start_button = Gtk.Button(label="Start")
        self.start_button.connect("clicked", self.on_start_button_clicked)
        self.hbox.pack_start(self.start_button, True, True, 0)

        self.stop_button = Gtk.Button(label="Stop")
        self.stop_button.connect("clicked", self.on_stop_button_clicked)
        self.hbox.pack_start(self.stop_button, True, True, 0)

        self.pause_button = Gtk.Button(label="Pause")
        self.pause_button.connect("clicked", self.on_pause_button_clicked)
        self.hbox.pack_start(self.pause_button, True, True, 0)

        self.resume_button = Gtk.Button(label="Resume")
        self.resume_button.connect("clicked", self.on_resume_button_clicked)
        self.hbox.pack_start(self.resume_button, True, True, 0)

        self.connect("delete-event", self.on_delete_event)

        self.gather_info()
        GLib.timeout_add_seconds(30, self.on_timeout)

    def on_toggle_button_clicked(self, widget):
        bus.call_async(bus_name, object_path, dbus_interface, 'toggle', '', [],
                       None, None)

    def on_start_button_clicked(self, widget):
        bus.call_async(bus_name, object_path, dbus_interface, 'start', '', [],
                       None, None)

    def on_stop_button_clicked(self, widget):
        bus.call_async(bus_name, object_path, dbus_interface, 'stop', '', [],
                       None, None)

    def on_pause_button_clicked(self, widget):
        bus.call_async(bus_name, object_path, dbus_interface, 'pause', '', [],
                       None, None)

    def on_resume_button_clicked(self, widget):
        bus.call_async(bus_name, object_path, dbus_interface, 'resume', '', [],
                       None, None)

    def update(self):
        text = 'Pomodoro:'

        try:
            if not self.is_running:
                text += ' (paused)'
        except:
            pass

        try:
            if self.is_working_time:
                text += ' Time to work'
            else:
                text += ' Time to procrastinate'
        except:
            pass

        try:
            more = ' (countdown: '
            more += "%.2f" % (self.current_countdown / 60)
            more += 'min)'
            text += more
            print(self.text)
        except:
            pass

        self.label.set_label(text)

    def on_is_running_result(self, is_running):
        self.is_running = is_running
        self.update()

    def on_is_working_time_result(self, is_working_time):
        self.is_working_time = is_working_time
        self.update()

    def on_current_countdown_result(self, current_countdown):
        self.current_countdown = current_countdown
        self.update()

    def on_delete_event(self, widget, event):
        self.hide()
        return True

    def gather_info(self):
        bus.call_async(bus_name, object_path, dbus_interface, 'is_running', '',
                       [], self.on_is_running_result, None)
        bus.call_async(bus_name, object_path, dbus_interface, 'is_working_time',
                       '', [], self.on_is_working_time_result, None)
        bus.call_async(bus_name, object_path, dbus_interface,
                       'current_countdown', '', [],
                       self.on_current_countdown_result, None)

    def on_timeout(self):
        self.gather_info()
        return True

window = PomodoroWindow()
window.show_all()

## The systray icon

class SystrayIcon:
    def __init__(self):
        self.systray_icon = Gtk.StatusIcon()
        self.systray_icon.set_tooltip_text('PyPomodoro')
        self.systray_icon.set_from_file(ICON_PATH)
        self.systray_icon.connect('activate', self.on_toggle_visibility)
        self.systray_icon.connect('popup-menu', self.on_popup_menu)

        self.menu = Gtk.Menu()

        toggle_visibility = Gtk.MenuItem("Show/Hide GUI")
        toggle_visibility.show()
        toggle_visibility.connect('activate', self.on_toggle_visibility)
        self.menu.append(toggle_visibility)

        exit_item = Gtk.MenuItem("Exit")
        exit_item.show()
        exit_item.connect('activate', self.on_exit_request)
        self.menu.append(exit_item)

    def on_toggle_visibility(self, widget):
        if window.get_visible():
            window.hide()
        else:
            window.show_all()

    def on_exit_request(self, widget):
        mainloop.quit();

    def on_popup_menu(self, icon, event_button, event_time):
        self.menu.popup(None, None, Gtk.StatusIcon.position_menu,
                        self.systray_icon, event_button, event_time)

systray_icon = SystrayIcon()

# The user's eye (text+desktop+gui notification)

def on_pomodoro_resumed_signal():
    resumed_msg.show()
    print(str(datetime.now()) + ': ' + resumed_msg.get_property('summary'))
    window.is_running = True
    window.update()

def on_pomodoro_paused_signal():
    paused_msg.show()
    print(str(datetime.now()) + ': ' + paused_msg.get_property('summary'))
    window.is_running = False
    window.update()

def on_work_session_started_signal():
    work_msg.show()
    print(str(datetime.now()) + ': ' + work_msg.get_property('summary'))
    window.gather_info()

def on_work_session_stopped_signal():
    procrastinate_msg.show()
    print(str(datetime.now()) + ': '
          + procrastinate_msg.get_property('summary'))
    window.gather_info()

bus.add_signal_receiver(on_pomodoro_resumed_signal,
                        signal_name='pomodoro_resumed',
                        dbus_interface=dbus_interface,
                        bus_name=bus_name, path=object_path)
bus.add_signal_receiver(on_pomodoro_paused_signal,
                        signal_name='pomodoro_paused',
                        dbus_interface=dbus_interface,
                        bus_name=bus_name, path=object_path)
bus.add_signal_receiver(on_work_session_started_signal,
                        signal_name='work_session_started',
                        dbus_interface=dbus_interface,
                        bus_name=bus_name, path=object_path)
bus.add_signal_receiver(on_work_session_stopped_signal,
                        signal_name='work_session_stopped',
                        dbus_interface=dbus_interface,
                        bus_name=bus_name, path=object_path)

# The main loop

mainloop.run()
