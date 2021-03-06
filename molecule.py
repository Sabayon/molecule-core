#!/usr/bin/python
# -*- coding: utf-8 -*-
#    Molecule Disc Image builder for Sabayon Linux
#    Copyright (C) 2009 Fabio Erculiani
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import os
import signal
import sys
sys.path.insert(0,'/usr/lib/molecule/')
sys.path.insert(0,'molecule/')
sys.path.insert(0,'.')
import molecule.cmdline
from molecule.handlers import Runner

parse_data = molecule.cmdline.parse()
if parse_data is None:
    raise SystemExit(1)
molecule_data, molecule_data_order = parse_data
if not molecule_data_order:
    molecule.cmdline.print_help()
    raise SystemExit(1)

for el in molecule_data_order:
    my = Runner(el, molecule_data.get(el))
    try:
        rc = my.run()
    except KeyboardInterrupt:
        while True:
            my.kill()
            break
        raise SystemExit(1)
    while True:
        my.kill()
        break
    if rc != 0:
        raise SystemExit(rc)
raise SystemExit(0)
