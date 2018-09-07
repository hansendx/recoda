""" Test the module that measures software projects. """

import glob
import os
import random
import re
import string
import tempfile
import unittest
from shutil import copy, rmtree

import pkg_resources
from recoda.analyse.python.metrics import (
    average_comment_density,
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
        # We cannot load all files from the test data directory.
        # We might have __init__.py and __pycache__ here.
        # This glob excludes those.
        # __init__.py needs to live in the data directories to include
        # the test data as package data.
        for _file in glob.glob(self._MOCK_DOCS_DIR+"/*[0-9]_[a-z]*"):
            # Filenames are in the Format
            # {correct measure}_{measured attribute}.{filetype to measure}
            _measure_value = re.sub(r'^(\d+)_.*', r'\1', os.path.basename(_file))
            _measured_attribute = re.sub(r'^\d+_(\w+)\.\w+$', r'\1', os.path.basename(_file))
            _filetype = re.sub(r'^\d+_\w+\.(\w+)$', r'\1', os.path.basename(_file))

            _mock_project_folder = "{tmp}/{measure_value}_{attribute}".format(
                tmp=_tmp_base_folder,
                measure_value=_measure_value,
                attribute=_measured_attribute
            )
            if not os.path.exists(_mock_project_folder):
                os.mkdir(_mock_project_folder)

            if _measured_attribute not in _docs_measures_dict:
                _docs_measures_dict[_measured_attribute] = {
                    _measure_value: _mock_project_folder
                }

            # We copy the mock file to the test area.
            # The copy is named as it would be in a real project.
            copy(_file, _mock_project_folder+"/README."+_filetype)

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
        # pkg_resources.resources_filename cashes files, when
        # in a compiled distribution. We need to clean up potentially
        # created files.
        pkg_resources.cleanup_resources()


class TestUnderstandability(unittest.TestCase):
    """ Test the functions measuring the understandability of code. """

    _MOCK_SCRIPTS_DIR = pkg_resources.resource_filename(
        'recoda.tests.data',
        'mock_scripts')

    def setUp(self):
        """ Set up mock project with documentation. """
        self._tmp_base_folder = tempfile.mkdtemp()


    def test_average_comment_density(self):
        """ Copy all test files into the test area, let them get measured and check measure. """
        _group_size = 0
        _total = 0

        _test_area = "{tmp_folder}/avgCD".format(
            tmp_folder=self._tmp_base_folder
        )
        os.makedirs(_test_area)

        # We calculate the average value for the test scripts and copy them
        # into the testing are.
        for _file in glob.glob(self._MOCK_SCRIPTS_DIR+"/*[0-9]_averageCD"):
            _group_size = _group_size + 1
            # Manually validated value is at the beginning of the file name.
            _measure = re.sub(r'^(\d+)_.*', r'\1', os.path.basename(_file))
            _total = _total + float(_measure)
            copy(
                _file,
                "{test_area}/{file_name}.py".format(
                    test_area=_test_area,
                    file_name=''.join( # A random 5 character long string as file name.
                        random.choices(string.ascii_uppercase + string.digits, k=5)
                    )
                )
            )

        _average_comment_density = float(_total / _group_size) / 100
        _test_average_comment_density = average_comment_density(_test_area)
        self.assertEqual(
            _average_comment_density,
            _test_average_comment_density
        )



    def tearDown(self):
        """ Clean Up """
        rmtree(self._tmp_base_folder)
        # pkg_resources.resources_filename cashes files, when
        # in a compiled distribution. We need to clean up potentially
        # created files.
        pkg_resources.cleanup_resources()
