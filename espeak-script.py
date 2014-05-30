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

import dbus
import dbus.mainloop.glib
from gi.repository import GObject
from espeak import espeak

mainloop = GObject.MainLoop()

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

bus = dbus.SessionBus()

bus_name = 'io.github.finna_pomodoro_project' #< The service name
object_path = '/io/github/finna_pomodoro_project/Pomodoro'
dbus_interface = 'io.github.finna_pomodoro_project.Pomodoro'

try:
    import getpass
    user = getpass.getuser()
except:
    user = 'Anonymous'

def available_slot():
    espeak.synth(user + ', time to procrastinate!')

def unavailable_slot():
    espeak.synth(user + ', time to work!')

bus.add_signal_receiver(available_slot,
                        signal_name='pomodoro_paused',
                        dbus_interface=dbus_interface, bus_name=bus_name,
                        path=object_path)
bus.add_signal_receiver(unavailable_slot,
                        signal_name='work_session_started',
                        dbus_interface=dbus_interface, bus_name=bus_name,
                        path=object_path)
bus.add_signal_receiver(available_slot,
                        signal_name='work_session_stopped',
                        dbus_interface=dbus_interface, bus_name=bus_name,
                        path=object_path)

mainloop.run()
