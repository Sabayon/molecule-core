# -*- coding: utf-8 -*-
import sys
sys.path.insert(0,'.')
sys.path.insert(0,'..')
import unittest

from molecule.compat import get_stringtype

class VersionTest(unittest.TestCase):

    def setUp(self):
        sys.stdout.write("%s called\n" % (self,))
        sys.stdout.flush()

    def tearDown(self):
        """
        tearDown is run after each test
        """
        sys.stdout.write("%s ran\n" % (self,))
        sys.stdout.flush()

    def test_version(self):

        from molecule.version import VERSION
        self.assert_(isinstance(VERSION, get_stringtype()))
        self.assert_(len(VERSION.split(".")) <= 4)
        self.assert_(len(VERSION.split(".")) >= 1)

if __name__ == '__main__':
    unittest.main()
    raise SystemExit(0)
