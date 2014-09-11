#!/usr/bin/env python3

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

import dbus
import dbus.mainloop.glib
from gi.repository import GObject

mainloop = GObject.MainLoop()

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

bus = dbus.SessionBus()

pomodoro_bus_name = 'io.github.finna_pomodoro_project' #< The service name
pomodoro_object_path = '/io/github/finna_pomodoro_project/Pomodoro'
pomodoro_dbus_interface = 'io.github.finna_pomodoro_project.Pomodoro'

pidgin_bus_name = 'im.pidgin.purple.PurpleService' #< The service name
pidgin_object_path = '/im/pidgin/purple/PurpleObject'
pidgin_dbus_interface = 'im.pidgin.purple.PurpleInterface'

pidgin_obj = bus.get_object(pidgin_bus_name, pidgin_object_path)
purple = dbus.Interface(pidgin_obj, pidgin_dbus_interface)

PIDGIN_STATUS_AVAILABLE = 2
PIDGIN_STATUS_UNAVAILABLE = 3

def available_slot():
    current = purple.PurpleSavedstatusGetMessage(purple.PurpleSavedstatusGetCurrent())
    status = purple.PurpleSavedstatusNew('', PIDGIN_STATUS_AVAILABLE)
    purple.PurpleSavedstatusSetMessage(status, current) 
    purple.PurpleSavedstatusActivate(status)

def unavailable_slot():
    current = purple.PurpleSavedstatusGetMessage(purple.PurpleSavedstatusGetCurrent())
    status = purple.PurpleSavedstatusNew('', PIDGIN_STATUS_UNAVAILABLE)
    purple.PurpleSavedstatusSetMessage(status, current) 
    purple.PurpleSavedstatusActivate(status)

bus.add_signal_receiver(available_slot,
                        signal_name='pomodoro_paused',
                        dbus_interface=pomodoro_dbus_interface,
                        bus_name=pomodoro_bus_name, path=pomodoro_object_path)
bus.add_signal_receiver(unavailable_slot,
                        signal_name='work_session_started',
                        dbus_interface=pomodoro_dbus_interface,
                        bus_name=pomodoro_bus_name, path=pomodoro_object_path)
bus.add_signal_receiver(available_slot,
                        signal_name='work_session_stopped',
                        dbus_interface=pomodoro_dbus_interface,
                        bus_name=pomodoro_bus_name, path=pomodoro_object_path)

def on_is_working_time_result(is_working_time):
    if is_working_time:
        unavailable_slot()
    else:
        available_slot()

def on_is_running_result(is_running):
    if is_running:
        bus.call_async(pomodoro_bus_name, pomodoro_object_path,
                       pomodoro_dbus_interface, 'is_working_time', '', [],
                       on_is_working_time_result, None)
    else:
        available_slot()

bus.call_async(pomodoro_bus_name, pomodoro_object_path, pomodoro_dbus_interface,
               'is_running', '', [], on_is_running_result, None)

mainloop.run()
