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

bus = dbus.SessionBus()
bus_name = 'io.github.finna_pomodoro_project' #< The service name
object_path = '/io/github/finna_pomodoro_project/Pomodoro'
dbus_interface = 'io.github.finna_pomodoro_project.Pomodoro'

try: 
    bus.call_blocking(bus_name, object_path, dbus_interface, 'toggle', '', [],
                      timeout=0.5)
except dbus.exceptions.DBusException:
    # Method doesn't have return, then it'll timeout
    pass
