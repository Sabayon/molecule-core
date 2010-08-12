# -*- coding: utf-8 -*-
import os
import sys
sys.path.insert(0,'.')
sys.path.insert(0,'..')
import unittest

class SpecsTest(unittest.TestCase):

    def setUp(self):
        sys.stdout.write("%s called\n" % (self,))
        sys.stdout.flush()

    def tearDown(self):
        """
        tearDown is run after each test
        """
        sys.stdout.write("%s ran\n" % (self,))
        sys.stdout.flush()

if __name__ == '__main__':
    unittest.main()
    raise SystemExit(0)
