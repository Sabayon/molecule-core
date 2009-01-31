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
import threading
from molecule.exception import SpecFileError, EnvironmentError
import molecule.utils

class Dictionary:

    def __init__(self):
        self._settings = {}
        self.L = threading.Lock()

    def __setitem__(self, key, value):
        with self.L:
            self._settings[key] = value

    def __getitem__(self, key):
        with self.L:
            return self._settings[key]

    def __contains__(self, key):
        with self.L:
            return key in self._settings

    def __cmp__(self, other):
        with self.L:
            return cmp(self._settings,other)

    def __str__(self):
        with self.L:
            return str(self._settings)

    def get(self, key):
        with self.L:
            return self._settings.get(key)

    def has_key(self, key):
        with self.L:
            return self._settings.has_key(key)

    def clear(self):
        with self.L:
            self._settings.clear()

    def keys(self):
        with self.L:
            return self._settings.keys()

class Constants(Dictionary):

    def __init__(self):
        Dictionary.__init__(self)
        self.load()

    def load(self):
        with self.L:
            ETC_DIR = '/etc'
            CONFIG_FILE_NAME = 'molecule.conf'

            mysettings = {
                'config_file': os.path.join(ETC_DIR, CONFIG_FILE_NAME),
            }

            self._settings.clear()
            self._settings.update(mysettings)

class Configuration(Dictionary):

    def __init__(self):
        Dictionary.__init__(self)
        self.Constants = Constants()
        self.load()

    def load(self, mysettings = {}):
        with self.L:
            settings = {
                'version': "0.1",
                'chroot_compressor': "mksquashfs",
                'iso_builder': "mkisofs",
                'iso_builder_builtin_args': ["-J","-R","-l","-no-emul-boot","-boot-load-size","4","-udf","-boot-info-table"],
            }
            self._settings.clear()
            self._settings.update(settings)
            self._settings.update(mysettings)

        paths_to_check = ["chroot_compressor","iso_builder"]
        for key in paths_to_check:
            molecule.utils.valid_exec_check(self.get(key))

class SpecParser:

    def __init__(self, filepath):

        def ne_string(x):
            return x

        def always_valid(*args):
            return True

        def valid_path(x):
            return os.path.lexists(x)

        def valid_file(x):
            return os.path.isfile(x)

        def valid_dir(x):
            return os.path.isdir(x)

        def ve_string_stripper(x):
            return x.strip()

        def ve_string_splitter(x):
            return x.strip().split()

        def valid_exec(x):
            molecule.utils.is_exec_available(x)
            return True

        def valid_ascii(x):
            try:
                x = str(x)
                return x
            except (UnicodeDecodeError,UnicodeEncodeError,):
                return ''

        def valid_path_string(x):
            try:
                os.path.split(x)
            except OSError:
                return False
            return True

        def valid_path_list(x):
            return [x for x in x.split(",") if valid_path_string(x)]

        self.vital_parameters = [
            "release_string",
            "source_chroot",
            "destination_iso_directory",
        ]
        self.parser_data_path = {
            'prechroot': {
                'cb': valid_exec,
                've': ve_string_stripper,
            },
            'release_string': {
                'cb': ne_string, # validation callback
                've': ve_string_stripper, # value extractor
            },
            'release_version': {
                'cb': ne_string,
                've': ve_string_stripper,
            },
            'release_desc': {
                'cb': ne_string,
                've': ve_string_stripper,
            },
            'release_file': {
                'cb': ne_string,
                've': ve_string_stripper,
            },
            'source_chroot': {
                'cb': valid_dir,
                've': ve_string_stripper,
            },
            'destination_chroot': {
                'cb': valid_path_string,
                've': ve_string_stripper,
            },
            'merge_destination_chroot': {
                'cb': valid_dir,
                've': ve_string_stripper,
            },
            'outer_chroot_script': {
                'cb': valid_exec,
                've': ve_string_stripper,
            },
            'inner_chroot_script': {
                'cb': valid_path_string,
                've': ve_string_stripper,
            },
            'destination_livecd_root': {
                'cb': valid_path_string,
                've': ve_string_stripper,
            },
            'merge_livecd_root': {
                'cb': valid_dir,
                've': ve_string_stripper,
            },
            'extra_mksquashfs_parameters': {
                'cb': always_valid,
                've': ve_string_splitter,
            },
            'extra_mkisofs_parameters': {
                'cb': always_valid,
                've': ve_string_splitter,
            },
            'destination_iso_directory': {
                'cb': valid_dir,
                've': ve_string_stripper,
            },
            'destination_iso_image_name': {
                'cb': valid_ascii,
                've': ve_string_stripper,
            },
            'directories_to_remove': {
                'cb': valid_path_list,
                've': ve_string_stripper,
            },
            'directories_to_empty': {
                'cb': valid_path_list,
                've': ve_string_stripper,
            },

        }

        self.filepath = filepath[:]

    def parse(self):
        mydict = {}
        data = self.__generic_parser(self.filepath)
        for line in data:
            try:
                key, value = line.split(":",1)
            except (ValueError, IndexError,):
                continue
            key = key.strip()
            check_dict = self.parser_data_path.get(key)
            if not isinstance(check_dict,dict): continue
            value = check_dict['ve'](value)
            if not check_dict['cb'](value): continue
            mydict[key] = value
        self.validate_parse(mydict)
        return mydict.copy()

    def validate_parse(self, mydata):
        for param in self.vital_parameters:
            if param not in mydata:
                raise SpecFileError("SpecFileError: '%s' missing or invalid '%s' parameter, it's vital. Your specification file is incomplete!" % (self.filepath,param,))

    def __generic_parser(self, filepath):
        with open(filepath,"r") as f:
            data = []
            content = f.readlines()
            f.close()
            # filter comments and white lines
            content = [x.strip().rsplit("#",1)[0].strip() for x in content if not x.startswith("#") and x.strip()]
            for line in content:
                if line in data: continue
                data.append(line)
            return data
