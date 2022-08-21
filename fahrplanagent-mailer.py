#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Fahrplan Agent - Informiert ueber DB Fahrplanaenderungen
#
#
# Copyright (C) 2017  Christoph Jacob (christoph.jacob@gmail.com)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import datetime
from io import StringIO
import subprocess

from fahrplanagent import ExpectedTrain, FahrplanAPI


# E-Mail-Adresse für Benachrichtigung
mailto = None

# Liste der Verbindungen, die überprüft werden
def trains():
    t = [
        ExpectedTrain('Berlin Hbf', 'Braunschweig Hbf', 'ICE 277', '6:30', '7:55', 13),
        ExpectedTrain('Berlin Hbf', 'Braunschweig Hbf', 'ICE 791', '7:33', '8:57', 14),

        ExpectedTrain('Braunschweig Hbf', 'Berlin Hbf', 'ICE 370', '16:01', '17:27', 7),
        ExpectedTrain('Braunschweig Hbf', 'Berlin Hbf', 'ICE 796', '17:02', '18:25', 7),
        ExpectedTrain('Braunschweig Hbf', 'Berlin Hbf', 'ICE 278', '18:01', '19:27', 7)
    ]
    return t


def main():
    api = FahrplanAPI()

    today = datetime.date.today()
    dd = today + datetime.timedelta(days=1)

    subject = "Fahrplan-Updates für " + dd.isoformat()

    if mailto is None:
        print(subject)
        print()
        f = None
    else:
        f = StringIO()

    all_ok = True
    for t in trains():
        t.check_for_date(api, dd)

        all_ok = all_ok and t.all_ok()
        t.print_info(file=f)
        t.print_status(file=f)
        print('', file=f)

    if (mailto is not None):
        p = subprocess.Popen(['mail', '-s '+subject, mailto], stdin=subprocess.PIPE)
        p.communicate(input=f.getvalue().encode('utf-8'))


if __name__ == "__main__":
    main()
