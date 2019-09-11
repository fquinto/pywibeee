#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Python testing library."""

import unittest
import pywibeee.main


class UnitTests(unittest.TestCase):
    """Provide tests."""

    def test_import(self):
        """Provide auto version test."""
        self.assertIsNotNone(pywibeee)

    def test_project(self):
        """Provide auto version test."""
        args = pywibeee.main.parsing_args(['--host', '192.168.1.150',
                                           '--get', 'status'])
        for i in range(0, 4):
            r = pywibeee.main.program(args, False)
            print(str(r))
        self.assertTrue(True)

    def test_auto_version(self):
        """Provide auto version test."""
        args = pywibeee.main.parsing_args(['--auto', '--get', 'version'])
        r = pywibeee.main.program(args, False)
        self.assertTrue('webversion' in str(r))

    def test_auto_models(self):
        """Provide auto model test."""
        models = ['WBM', 'WBT', 'WMX', 'WTD', 'WX2', 'WX3', 'WXX',
                  'WBB', 'WB3', 'W3P', 'WGD', 'WBP']
        args = pywibeee.main.parsing_args(['--auto', '--get', 'model',
                                           '-o', 'plain'])
        r = pywibeee.main.program(args, False)
        self.assertTrue(str(r) in models)


if __name__ == '__main__':
    unittest.main()
