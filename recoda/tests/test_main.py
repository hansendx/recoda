""" Test the main module of ReCodA. """

import sys
import tempfile
import unittest
from unittest.mock import patch

import pandas

import recoda.__main__ as main
from recoda.project_handler import git
from recoda.tests.helpers import (
    create_test_repositories,
    remove_test_repositories
)


class TestArgumentParser(unittest.TestCase):
    """ Ensure the argument Parser works as expected. """

    def setUp(self):
        """ Set some common variables. """
        self.name = main.__name__
        self.base_dir = {'long': '--base-dir', 'short': '-b'}
        self.type = {'long': '--project-type', 'short': '-t'}
        self.language = {'long': '--language', 'short': '-l'}
        self.langauge_param = 'python'
        self.fake_path_param = '/some/dir'

    def test_base_dir_argument(self):
        """ Can we pass --base-dir -b Argument and get back the value? """
        _arguments_long = [
            self.name,
            self.base_dir['long'],
            self.fake_path_param,
            self.language['long'],
            self.langauge_param
        ]
        _arguments_short = [
            self.name,
            self.base_dir['short'],
            self.fake_path_param,
            self.language['short'],
            self.langauge_param
        ]
        with patch.object(sys, 'argv', _arguments_long):
            _argparser = main.parse_arguments()
            self.assertEqual(_argparser.base_dir, self.fake_path_param)
            self.assertEqual(_argparser.language, self.langauge_param)
        with patch.object(sys, 'argv', _arguments_short):
            _argparser = main.parse_arguments()
            self.assertEqual(_argparser.base_dir, self.fake_path_param)
            self.assertEqual(_argparser.language, self.langauge_param)

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
        _arguments_base = [
            self.name,
            self.base_dir['short'],
            self.fake_path_param,
            self.language['short'],
            self.langauge_param
        ]

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

class TestMeasureProjects(unittest.TestCase):
    """ We make sure the measure_projects function returns an expected pandas dataframe. """

    def setUp(self):
        """ Set up mock projects. """
        # Working in a tmp folder so we dont have juggle to much with paths
        # and dont risk cluttering the package directory.
        self.base_folder = tempfile.mkdtemp()
        self.projects = create_test_repositories(self.base_folder)

        self.handler = git.Handler(self.base_folder)

    def test_measure_projects(self):
        """ The dataframe should have a column for the ids of the projects.
        If it is actually filled with measurements is to be measured elsewhere. #TODO
        """
        _test_object = main.MeasureProjects(project_measure_handler=self.handler, language='python')
        _test_output = _test_object.measure()
        # Do we get a pandas dataframe?
        self.assertIsInstance(_test_output, pandas.DataFrame)
        # Do we have an id column?
        self.assertIn('id', list(_test_output.columns.values))
        # Doe we have all project ids?
        _id_list = _test_output['id'].tolist()
        for _project in self.handler.get_project_objects():
            self.assertIn(
                self.handler.get_identifier(_project),
                _id_list
            )

    def tearDown(self):
        remove_test_repositories(self.base_folder)
