#!/usr/bin/python -O
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
from molecule.i18n import _
from molecule.output import brown, darkgreen
from molecule.specs.skel import GenericExecutionStep


class Runner(GenericExecutionStep):

    def __init__(self, spec_path, metadata):
        GenericExecutionStep.__init__(self, spec_path, metadata)
        self.execution_order = metadata['__plugin__'].get_execution_steps()

    def pre_run(self):
        return 0

    def post_run(self):
        return 0

    def kill(self, success = True):
        return 0

    def run(self):

        self.pre_run()
        count = 0
        maxcount = len(self.execution_order)
        self.Output.updateProgress( "[%s|%s] %s" % (
            darkgreen("Runner"),brown(self.spec_name),
            _("preparing execution"),), count = (count,maxcount,)
        )
        for myclass in self.execution_order:

            count += 1
            self.Output.updateProgress( "[%s|%s] %s %s" % (
                darkgreen("Runner"),brown(self.spec_name),_("executing"),
                str(myclass),), count = (count,maxcount,)
            )
            my = myclass(self.spec_path, self.metadata)

            rc = 0
            while 1:

                try:
                    # pre-run
                    rc = my.pre_run()
                    if rc:
                        break
                    # run
                    rc = my.run()
                    if rc:
                        break
                    # post-run
                    rc = my.post_run()
                    if rc:
                        break

                    break
                except:
                    my.kill(success = False)
                    raise

            my.kill(success = rc == 0)
            if rc:
                return rc

        self.post_run()
        self.Output.updateProgress( "[%s|%s] %s" % (
                darkgreen("Runner"),brown(self.spec_name),
                _("All done"),
            )
        )
        return 0
