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
import molecule.utils

class GenericSpecFunctions:

    def ne_string(self, x):
        return x, 'raw_unicode_escape'

    def ne_list(self, x):
        return x

    def always_valid(self, *args):
        return True

    def valid_path(self, x):
        return os.path.lexists(x)

    def valid_file(self, x):
        return os.path.isfile(x)

    def valid_dir(self, x):
        return os.path.isdir(x)

    def ve_string_stripper(self, x):
        return unicode(x,'raw_unicode_escape').strip()

    def ve_string_splitter(self, x):
        return unicode(x,'raw_unicode_escape').strip().split()

    def valid_exec(self, x):
        molecule.utils.is_exec_available(x)
        return x

    def valid_exec_first_list_item(self, x):
        if not x:
            return False
        myx = x[0]
        molecule.utils.is_exec_available(myx)
        return True

    def valid_ascii(self, x):
        try:
            x = str(x)
            return x
        except (UnicodeDecodeError,UnicodeEncodeError,):
            return ''

    def valid_path_string(self, x):
        try:
            os.path.split(x)
        except OSError:
            return False
        return True

    def valid_path_list(self, x):
        return [y.strip() for y in \
            unicode(x,'raw_unicode_escape').split(",") if \
                valid_path_string(y) and y.strip()]

class GenericSpec(GenericSpecFunctions):

    EXECUTION_STRATEGY_KEY = "execution_strategy"

    @staticmethod
    def execution_strategy():
        """
        Return a string that describes the supported execution strategy.
        Such as "remaster", "livecd", etc.

        @return: execution strategy string id
        @rtype: string
        """
        raise NotImplementedError()

    def vital_parameters(self):
        """
        Return a list of vital .spec file parameters

        @return: list of vital .spec file parameters
        @rtype: list
        """
        raise NotImplementedError()

    def parser_data_path(self):
        """
        Return a dictionary containing parameter names as key and
        dict containing keys 've' and 'cb' which values are three
        callable functions that respectively do value extraction (ve),
        value verification (cb) and value modding (mod).

        @return: data path dictionary (see ChrootSpec code for more info)
        @rtype: dict
        """
        raise NotImplementedError()

class LivecdSpec(GenericSpec):

    @staticmethod
    def execution_strategy():
        return "livecd"

    def vital_parameters(self):
        return [
            "release_string",
            "source_chroot",
            "destination_iso_directory",
            "destination_livecd_root",
        ]

    def parser_data_path(self):
        return {
            'prechroot': {
                'cb': self.valid_exec_first_list_item,
                've': self.ve_string_splitter,
            },
            'release_string': {
                'cb': self.ne_string, # validation callback
                've': self.ve_string_stripper, # value extractor
            },
            'release_version': {
                'cb': self.ne_string,
                've': self.ve_string_stripper,
            },
            'release_desc': {
                'cb': self.ne_string,
                've': self.ve_string_stripper,
            },
            'release_file': {
                'cb': self.ne_string,
                've': self.ve_string_stripper,
            },
            'source_chroot': {
                'cb': self.valid_dir,
                've': self.ve_string_stripper,
            },
            'destination_chroot': {
                'cb': self.valid_path_string,
                've': self.ve_string_stripper,
            },
            'extra_rsync_parameters': {
                'cb': self.valid_path_string,
                've': self.ve_string_splitter,
            },
            'merge_destination_chroot': {
                'cb': self.valid_dir,
                've': self.ve_string_stripper,
            },
            'outer_chroot_script': {
                'cb': self.valid_exec,
                've': self.ve_string_stripper,
            },
            'inner_chroot_script': {
                'cb': self.valid_path_string,
                've': self.ve_string_stripper,
            },
            'destination_livecd_root': {
                'cb': self.valid_path_string,
                've': self.ve_string_stripper,
            },
            'merge_livecd_root': {
                'cb': self.valid_dir,
                've': self.ve_string_stripper,
            },
            'extra_mksquashfs_parameters': {
                'cb': self.always_valid,
                've': self.ve_string_splitter,
            },
            'extra_mkisofs_parameters': {
                'cb': self.always_valid,
                've': self.ve_string_splitter,
                'mod': self.ve_string_splitter,
            },
            'pre_iso_script': {
                'cb': self.valid_exec,
                've': self.ve_string_stripper,
            },
            'destination_iso_directory': {
                'cb': self.valid_dir,
                've': self.ve_string_stripper,
            },
            'destination_iso_image_name': {
                'cb': self.valid_ascii,
                've': self.ve_string_stripper,
            },
            'paths_to_remove': {
                'cb': self.ne_list,
                've': self.valid_path_list,
            },
            'paths_to_empty': {
                'cb': self.ne_list,
                've': self.valid_path_list,
            },

        }




# FIXME: this will need to be pluggable (and plugin factory is required)
SPEC_PLUGS = dict((x.execution_strategy(), x,) for x in \
    (LivecdSpec, RemasterSpec))
