""" Test the module that measures software projects. """

import glob
import os
import random
import re
import string
import tempfile
import unittest
from shutil import copy, rmtree, copytree

import pkg_resources

import pipreqs.pipreqs as pipreqs
from recoda.analyse.python.metrics import (
    average_comment_density,
    project_readme_size,
    requirements_declared
)


# Tests functions in the _installability module.
# class TestPackageable(unittest.TestCase):
#     """ Test the function measuring the packageability. """


#     _MOCK_SETUP_DIR = pkg_resources.resource_filename(
#         'recoda.tests.data',
#         'mock_setup_py')

#     def setUp(self):
#         """ Create two mock packages with setup scripts to measure. """
#         _tmp_base_folder = tempfile.mkdtemp()

#         _scored_setup_dict = {}
#         for _file in glob.glob(self._MOCK_SETUP_DIR+"/*setup_py", recursive=True):
#             _score = re.match(r'^\d+', os.path.basename(_file))[0]
#             _mock_project_folder = "{tmp}/{score}_py".format(
#                 tmp=_tmp_base_folder,
#                 score=_score
#             )
#             os.mkdir(_mock_project_folder)

#             _scored_setup_dict[_score] = _mock_project_folder

#             copy(_file, _scored_setup_dict[_score]+'/setup.py')

#         # pkg_resources.resources_filename cashes files, when
#         # in a compiled distribution. We need to clean up potentially
#         # created files.
#         pkg_resources.cleanup_resources()

#         self._tmp_base_folder = _tmp_base_folder
#         self._scored_setup_dict = _scored_setup_dict

#     def test_scoring(self):
#         """ Compare the validated scores with packageable scores. """
#         for _score, _folder in self._scored_setup_dict.items():
#             _test_score = packageability(_folder)
#             self.assertEqual(int(_score), _test_score)

#     def tearDown(self):
#         """ Clean up. """
#         rmtree(self._tmp_base_folder)

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

class TestRequirementsDeclared(unittest.TestCase):
    """ Test the functions for the installability metrics. """

    def setUp(self):
        """ Create a copy of this package to use it as test data. """
        _this_package = pkg_resources.resource_filename('recoda', '')
        self.this_package_basename = os.path.basename(_this_package)
        self.test_sandbox = tempfile.mkdtemp()
        self.requirements_filename = 'requirements.txt'
        self.import_list = pipreqs.get_all_imports(path=_this_package)
        copytree(_this_package, self.test_sandbox+'/'+self.this_package_basename)

    def test_score_from_requirements_file(self):
        """ Do we get a score when requirements are declared in the requirements.txt"""
        
        # Test all requirements correctly declared
        with open(
            '{}/{}'.format(self.test_sandbox, self.requirements_filename), 'w'
        ) as requirements_mock_file:
            requirements_mock_file.write('\n'.join(self.import_list))

        # All requirements declared should yield 100% i.e. 1
        self.assertEqual(
            1,
            requirements_declared(self.test_sandbox)
        )

        # Test requirements file with one missing dependency
        with open( '{}/{}'.format( self.test_sandbox, self.requirements_filename), 'w'
        ) as requirements_mock_file:
            requirements_mock_file.write('\n'.join(self.import_list[1:]))

        _percentage_of_requirements_declared = float(len(self.import_list) -1) / len(self.import_list) 
        self.assertEqual(
            _percentage_of_requirements_declared,
            requirements_declared(self.test_sandbox)
        )

    def test_from_setup_script(self):
        """ Do we get expected behavior, if requirements are in the setup.py

        There can be either no requirements.txt file or a file containing only a "."
        character. We test for both setups.
        """
        _full_path='{dirname}/{filename}'

        _setup_mock_content = (
        "from distutils.core import setup\n"
        "setup(\n"
        "    name='stub',\n"
        "    install_requires=[\n"
        "        {requirements}\n"
        "    ]\n"
        ")"
        )

        _quoted_import_list=["\""+item+"\"" for item in self.import_list[1:]]
        _requirements_array_string = ',\n'.join(_quoted_import_list)

        # Test requirements file with one missing dependency
        with open(
            _full_path.format(
                dirname=self.test_sandbox,
                filename='setup.py'),
            'w'
        ) as requirements_mock_file:
            requirements_mock_file.write(
                _setup_mock_content.format(
                    requirements=_requirements_array_string)
            )

        _percentage_of_requirements_declared = float(len(self.import_list) -1) / float(len(self.import_list)) 
        self.assertEqual(
            _percentage_of_requirements_declared,
            requirements_declared(self.test_sandbox)
        )




    def tearDown(self):
        """ Clean up the sandbox. """
        rmtree(self.test_sandbox, ignore_errors=True)
        # pkg_resources.resources_filename cashes files, when
        # in a compiled distribution. We need to clean up potentially
        # created files.
        pkg_resources.cleanup_resources()
        