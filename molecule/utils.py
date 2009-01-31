#!/usr/bin/python -O
# -*- coding: iso-8859-1 -*-
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

from __future__ import with_statement
import os
import time
import subprocess
from molecule.exception import EnvironmentError

def get_year():
    return time.strftime("%Y")

def valid_exec_check(path):
    with open("/dev/null","w") as f:
        p = subprocess.Popen([path], stdout = f, stderr = f)
        rc = p.wait()
        if rc == 127:
            raise EnvironmentError("EnvironmentError: %s not found" % (path,))

def is_exec_available(exec_name):
    paths = os.getenv("PATH")
    if not paths: return False
    paths = paths.split(":")
    for path in paths:
        path = os.path.join(path,exec_name)
        if os.path.isfile(path) and os.access(path,os.X_OK):
            return True
    return False
