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
import sys
import molecule.utils
import molecule.output
from molecule.i18n import _
from molecule.settings import SpecParser, Configuration

def parse():

    args_to_remove = ["--nocolor"]
    data = {}

    myargs = sys.argv[1:]

    if "--help" in myargs:
        return data, []
    if "--nocolor" in myargs:
        molecule.output.nocolor()

    for arg in args_to_remove:
        if arg in myargs:
            myargs.remove(arg)

    data_order = []
    for el in myargs:
        if os.path.isfile(el) and os.access(el, os.R_OK):
            obj = SpecParser(el)
            el_data = obj.parse()
            del obj
            if el_data:
                data_order.append(el)
                data[el] = el_data
    return data, data_order

def print_help():
    config = Configuration()
    help_data = [
        None,
        (0, " ~ Molecule %s ~ " % (config.get('version'),), 1,
            'Disc Image builder for Sabayon Linux - (C) %s' % (
                molecule.utils.get_year(),) ),
        None,
        (0, _('Basic Options'), 0, None),
        None,
        (1, '--help', 2, _('this output')),
        (1, '--nocolor', 1, _('disable colorized output')),
        None,
        (0, _('Application Options'), 0, None),
        (1, '<spec file path 1> <spec file path 2> ...', 1,
            _('execute against specified specification files')),
        None,
    ]
    molecule.output.print_menu(help_data)
