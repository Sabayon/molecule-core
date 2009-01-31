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

class MoleculeException(Exception):
    """General superclass for Entropy exceptions"""
    def __init__(self,value):
        self.value = value[:]

    def __str__(self):
        if isinstance(self.value, basestring):
            return self.value
        else:
            return repr(self.value)

class EnvironmentError(MoleculeException):
        """Environment error, self explanatory"""

class SpecFileError(MoleculeException):
        """Error inside spec file"""