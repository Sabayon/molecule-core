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
from molecule.i18n import _
from molecule.output import red, brown, blue, green, purple, darkgreen, darkred, bold, darkblue, readtext
from molecule.exception import EnvironmentError, NotImplementedError

# This is an interface that has to be reimplemented in order to make it doing something useful
class GenericHandlerInterface:

    def __init__(self, spec_path, metadata):
        from molecule import Output, Config
        self.Output = Output
        self.Config = Config
        self.spec_path = spec_path
        self.metadata = metadata
        self.spec_name = os.path.basename(self.spec_path)

    def pre_run(self):
        raise NotImplementedError("NotImplementedError: this needs to be reimplemented")

    def run(self):
        raise NotImplementedError("NotImplementedError: this needs to be reimplemented")

    def post_run(self):
        raise NotImplementedError("NotImplementedError: this needs to be reimplemented")

    def kill(self):
        raise NotImplementedError("NotImplementedError: this needs to be reimplemented")

class MirrorHandler(GenericHandlerInterface):

    def __init__(self, *args, **kwargs):
        GenericHandlerInterface.__init__(self, *args, **kwargs)

    def pre_run(self):
        self.Output.updateProgress( "[%s|%s] %s" % (blue("MirrorHandler"),darkred(self.spec_name),_("executing pre_run"),))
        return 0

    def post_run(self):
        self.Output.updateProgress( "[%s|%s] %s" % (blue("MirrorHandler"),darkred(self.spec_name),_("executing post_run"),))
        return 0

    def kill(self):
        self.Output.updateProgress( "[%s|%s] %s" % (blue("MirrorHandler"),darkred(self.spec_name),_("executing kill"),))
        return 0

    def run(self):
        self.Output.updateProgress( "[%s|%s] %s" % (blue("MirrorHandler"),darkred(self.spec_name),_("executing run"),))
        # running the syncer
        source_dir = self.metadata['source_chroot']
        dest_dir = os.path.join(self.metadata['destination_chroot'],os.path.basename(source_dir))
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir,0755)
        # FIXME: complete this
        return 0

class ChrootHandler(GenericHandlerInterface):

    def __init__(self, *args, **kwargs):
        GenericHandlerInterface.__init__(self, *args, **kwargs)

    def pre_run(self):
        self.Output.updateProgress( "[%s|%s] %s" % (blue("ChrootHandler"),darkred(self.spec_name),_("executing pre_run"),))
        return 0

    def post_run(self):
        self.Output.updateProgress( "[%s|%s] %s" % (blue("ChrootHandler"),darkred(self.spec_name),_("executing post_run"),))
        return 0

    def kill(self):
        self.Output.updateProgress( "[%s|%s] %s" % (blue("ChrootHandler"),darkred(self.spec_name),_("executing kill"),))
        return 0

    def run(self):
        self.Output.updateProgress( "[%s|%s] %s" % (blue("ChrootHandler"),darkred(self.spec_name),_("executing run"),))
        return 0


class Runner(GenericHandlerInterface):

    def __init__(self, spec_path, metadata):
        GenericHandlerInterface.__init__(self, spec_path, metadata)
        self.execution_order = [MirrorHandler,ChrootHandler]

    def pre_run(self):
        return 0

    def post_run(self):
        return 0

    def kill(self):
        return 0

    def run(self):

        self.pre_run()
        count = 0
        maxcount = len(self.execution_order)
        self.Output.updateProgress( "[%s|%s] %s" % (darkgreen("Runner"),brown(self.spec_name),_("preparing execution"),), count = (count,maxcount,))
        for myclass in self.execution_order:

            count += 1
            self.Output.updateProgress( "[%s|%s] %s %s" % (darkgreen("Runner"),brown(self.spec_name),_("executing"),str(myclass),), count = (count,maxcount,))
            my = myclass(self.spec_path, self.metadata)

            rc = 0
            while 1:
                # pre-run
                rc = my.pre_run()
                if rc: break
                # run
                rc = my.run()
                if rc: break
                # post-run
                rc = my.post_run()
                if rc: break
                break

            my.kill()
            if rc: return rc

        self.post_run()
        self.Output.updateProgress( "[%s|%s] %s!" % (darkgreen("Runner"),brown(self.spec_name),_("All done"),))
        return 0



