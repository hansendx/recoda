""" Test the main module of the ReCodA. """

import argparse
import logging
import sys
import unittest
from unittest.mock import patch

import recoda.__main__ as main


class TestArgumentParser(unittest.TestCase):
    """ Ensure the argument Parser works as expected. """

    def setUp(self):
        """ Set some common variables. """
        self.name = main.__name__
        self.base_dir = {'long': '--base-dir', 'short': '-b'}
        self.type = {'long': '--project-type', 'short': '-t'}
        self.fake_path = '/some/dir'


    def test_base_dir_argument(self):
        """ Can we pass --base-dir -b Argument and get back the value? """
        _arguments_long = [self.name, self.base_dir['long'], self.fake_path]
        _arguments_short = [self.name, self.base_dir['short'], self.fake_path]
        with patch.object(sys, 'argv', _arguments_long):
            _argparser = main.parse_arguments()
            self.assertEqual(_argparser.base_dir, self.fake_path)
        with patch.object(sys, 'argv', _arguments_short):
            _argparser = main.parse_arguments()
            self.assertEqual(_argparser.base_dir, self.fake_path)

    def test_base_dir_mandatory(self):
        """ We make sure that --base-dir is mandatory.

        We cannot gather project folder if we do not know where to start. 
        """
        # argparse will try to access argv[0] so we need to supply an argv
        # of length > 0 to avoid an IndexError.
        with patch.object(sys, 'argv', main.__name__):
            with self.assertRaises(SystemExit):
                _argparser = main.parse_arguments()

    def test_repository_type(self):
        """ Can we pass a project type switch -t --project-type? """
        # Lets us parse through the viable options with minimal redundancy.
        _types = {'git': 'git', 'dir': 'directory'}
        _arguments_base = [self.name, self.base_dir['short'], self.fake_path]

        # directory should be the default, since directories are probable to exist
        # in the base directory. 
        with patch.object(sys, 'argv', _arguments_base):
            _argparser = main.parse_arguments()
            self.assertEqual(_argparser.project_type, _types['dir'])
        
        for _type in _types:
            _arguments = _arguments_base.copy()
            _arguments.extend(['-t', _types[_type]])
            with patch.object(sys, 'argv', _arguments):
                _argparser = main.parse_arguments()
                self.assertEqual(_argparser.project_type, _types[_type])

        # We only allow the types in _types everything else should
        # be caught by the argument parser as wrong value.
        _no_type = 'svn'
        _arguments = _arguments_base.copy()
        _arguments.extend(['-t', _no_type])
        with patch.object(sys, 'argv', _arguments):
            with self.assertRaises(SystemExit):
                _argparser = main.parse_arguments()
