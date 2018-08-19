""" Test the module that measures software projects. """

import os
import unittest
import tempfile
import pkg_resources
import glob
import re

from recoda.analyse.python.metrics import (
    packageability
)


class TestPackageable(unittest.TestCase):
    """ Test the function measuring the packageability. """


    _MOCK_SETUP_DIR = pkg_resources.resource_filename(
        'recoda.tests.data',
        'mock_setup_py')

    def setUp(self):
        """ Create two setup scripts to measure. """
        # TODO This should be possible to be more elegant.
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

        self._scored_setup_dict = _scored_setup_dict

    def test_scoring(self):
        """ Compare the validated scores with packageable scores. """
        for _score, _folder in self._scored_setup_dict.items():
            _test_score = packageability(_folder)
            self.assertEqual(int(_score), _test_score)
