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

class Constants(dict):

    def __init__(self):
        dict.__init__(self)
        self.load()

    def load(self):
        ETC_DIR = '/etc'
        CONFIG_FILE_NAME = 'molecule.conf'

        mysettings = {
            'config_file': os.path.join(ETC_DIR, CONFIG_FILE_NAME),
        }

        self.clear()
        self.update(mysettings)

class Configuration(dict):

    def __init__(self):
        dict.__init__(self)
        self.Constants = Constants()
        self.load()

    def load(self, mysettings = {}):
        settings = {
            'version': "0.1",
            'chroot_compressor': "mksquashfs",
            'iso_builder': "mkisofs",
            'mirror_syncer': "rsync",
            'chroot_compressor_builtin_args': ["-noappend"],
            'iso_builder_builtin_args': ["-J","-R","-l","-no-emul-boot","-boot-load-size","4","-udf","-boot-info-table"],
            'mirror_syncer_builtin_args': ["-a","--delete","--delete-excluded","--numeric-ids"],
            'chroot_compressor_output_file': "livecd.squashfs",
        }
        self.clear()
        self.update(settings)
        self.update(mysettings)

        paths_to_check = ["chroot_compressor","iso_builder","mirror_syncer"]
        for key in paths_to_check:
            molecule.utils.valid_exec_check(self.get(key))

class SpecParser:

    def __init__(self, filepath):

        def ne_string(x):
            return x,'raw_unicode_escape'

        def ne_list(x):
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
            return unicode(x,'raw_unicode_escape').strip()

        def ve_string_splitter(x):
            return unicode(x,'raw_unicode_escape').strip().split()

        def valid_exec(x):
            molecule.utils.is_exec_available(x)
            return x

        def valid_exec_first_list_item(x):
            if not x: return False
            myx = x[0]
            molecule.utils.is_exec_available(myx)
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
            return [y.strip() for y in unicode(x,'raw_unicode_escape').split(",") if valid_path_string(y) and y.strip()]

        self.vital_parameters = [
            "release_string",
            "source_chroot",
            "destination_iso_directory",
            "destination_livecd_root",
        ]
        self.parser_data_path = {
            'prechroot': {
                'cb': valid_exec_first_list_item,
                've': ve_string_splitter,
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
            'extra_rsync_parameters': {
                'cb': valid_path_string,
                've': ve_string_splitter,
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
                'mod': ve_string_splitter,
            },
            'pre_iso_script': {
                'cb': valid_exec,
                've': ve_string_stripper,
            },
            'destination_iso_directory': {
                'cb': valid_dir,
                've': ve_string_stripper,
            },
            'destination_iso_image_name': {
                'cb': valid_ascii,
                've': ve_string_stripper,
            },
            'paths_to_remove': {
                'cb': ne_list,
                've': valid_path_list,
            },
            'paths_to_empty': {
                'cb': ne_list,
                've': valid_path_list,
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
                raise SpecFileError(
                    "SpecFileError: '%s' missing or invalid"
                    " '%s' parameter, it's vital. Your specification"
                    " file is incomplete!" % (self.filepath,param,)
                )

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
