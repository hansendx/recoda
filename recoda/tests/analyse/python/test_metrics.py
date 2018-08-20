""" Test the module that measures software projects. """

import glob
import os
import re
import tempfile
import unittest
from shutil import copy, rmtree

import pkg_resources

from recoda.analyse.python.metrics import (
    packageability,
    project_readme_size
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

            copy(_file, _scored_setup_dict[_score]+'/setup.py')

        # pkg_resources.resources_filename cashes files, when
        # in a compiled distribution. We need to clean up potentially
        # created files.
        pkg_resources.cleanup_resources()

        self._tmp_base_folder = _tmp_base_folder
        self._scored_setup_dict = _scored_setup_dict

    def test_scoring(self):
        """ Compare the validated scores with packageable scores. """
        for _score, _folder in self._scored_setup_dict.items():
            _test_score = packageability(_folder)
            self.assertEqual(int(_score), _test_score)

    def tearDown(self):
        """ Clean up. """
        rmtree(self._tmp_base_folder)

class TestLearnability(unittest.TestCase):
    """ Test the functions measuring Learnability of software projects. """

    _MOCK_DOCS_DIR = pkg_resources.resource_filename(
        'recoda.tests.data',
        'mock_docs')

    def setUp(self):
        """ Set up mock project with documentation. """
        _tmp_base_folder = tempfile.mkdtemp()

        _docs_measures_dict = {}
        # We might have __init__.py and __pycache__ here.
        # This glob excludes those.
        for _file in glob.glob(self._MOCK_DOCS_DIR+"/*[0-9]_[a-z]*"):
            _measure = re.sub(r'^(\d+)_.*', r'\1', os.path.basename(_file))
            _measured_attribute = re.sub(r'^\d+_(\w+)$', r'\1', os.path.basename(_file))

            _mock_project_folder = "{tmp}/{measure}_{attribute}".format(
                tmp=_tmp_base_folder,
                measure=_measure,
                attribute=_measured_attribute
            )
            os.mkdir(_mock_project_folder)

            if _measured_attribute not in _docs_measures_dict:
                _docs_measures_dict[_measured_attribute] = {
                    _measure: _mock_project_folder
                }

            copy(_file, _mock_project_folder+"/README.md")

        # pkg_resources.resources_filename cashes files, when
        # in a compiled distribution. We need to clean up potentially
        # created files.
        pkg_resources.cleanup_resources()
        self._tmp_base_folder = _tmp_base_folder
        self._docs_measures_dict = _docs_measures_dict

    def test_readme_size(self):
        """ We want a function, that returns the word count of the root README.

        It should not measure readme files in subfolders.
        The main, that explains the project should be at the root of it.
        """

        _word_count_projects = self._docs_measures_dict['words']

        for _measure, _folder in _word_count_projects.items():
            self.assertEqual(
                int(_measure),
                project_readme_size(_folder)
            )

    def tearDown(self):
        """ Clean Up """
        rmtree(self._tmp_base_folder)
