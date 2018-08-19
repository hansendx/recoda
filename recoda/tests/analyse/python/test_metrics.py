""" Test the module that measures software projects. """

import os
import unittest
import tempfile
import pkg_resources
import glob
import re
from shutil import rmtree

from recoda.analyse.python.metrics import (
    packageability
)

# Tests functions in the _installability module. 
class TestPackageable(unittest.TestCase):
    """ Test the function measuring the packageability. """


    _MOCK_SETUP_DIR = pkg_resources.resource_filename(
        'recoda.tests.data',
        'mock_setup_py')

    def setUp(self):
        """ Create two mock packages with setup scripts to measure. """
        _tmp_base_folder = tempfile.mkdtemp()

        _scored_setup_dict = {}
        for _file in glob.glob(self._MOCK_SETUP_DIR+"/*setup_py", recursive=True):
            _score = re.match(r'^\d+', os.path.basename(_file))[0]
            _mock_project_folder = "{tmp}/{score}_py".format(
                tmp=_tmp_base_folder,
                score=_score
            )
            os.mkdir(_mock_project_folder)

            _scored_setup_dict[_score] = _mock_project_folder

            with open(_file, 'r') as mock_setup_py:
                with open(_scored_setup_dict[_score]+'/setup.py', 'w') as setup_py:
                    setup_py.write(mock_setup_py.read())

        pkg_resources.cleanup_resources()

        self._tmp_base_folder = _tmp_base_folder
        self._scored_setup_dict = _scored_setup_dict

    def test_scoring(self):
        """ Compare the validated scores with packageable scores. """
        for _score, _folder in self._scored_setup_dict.items():
            _test_score = packageability(_folder)
            self.assertEqual(int(_score), _test_score)
            _test_score = packageability(_folder)
            self.assertEqual(int(_score), _test_score)

    def tearDown(self):
        """ Clean up. """
        rmtree(self._tmp_base_folder)
        

class TestLearnability(unittest.TestCase):
    """ Test the functions measuring Learnability of software projects. """

    setUp
