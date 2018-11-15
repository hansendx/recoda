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

from pipreqs import pipreqs
from recoda.analyse.python.metrics import (
    average_comment_density,
    standard_compliance,
    project_readme_size,
    project_doc_size,
    requirements_declared,
    license_type,
    testlibrary_usage,
    error_density,
    docker_setup,
    singularity_setup,
    packageability
)


class TestLearnability(unittest.TestCase):
    """ Test the functions measuring Learnability of software projects. """

    _MOCK_DOCS_DIR = pkg_resources.resource_filename(
        'recoda.tests.data',
        'mock_docs')

    def setUp(self):
        """ Set up mock project with documentation. """
        _tmp_base_folder = tempfile.mkdtemp()
        self._measures = {
            'doc_words': 0,
            'readme_words': 0
        }
        self._readme_folder = ''

        _docs_measures_dict = {}
        # We cannot load all files from the test data directory.
        # We might have __init__.py and __pycache__ here.
        # This glob excludes those.
        # __init__.py needs to live in the data directories to include
        # the test data as package data.
        for _file in glob.glob(self._MOCK_DOCS_DIR+"/*[0-9]_[a-z]*"):
            # Filenames are in the Format
            # {correct measure}_{measured attribute}.{filetype to measure}
            _measure_value = int(re.sub(r'^(\d+)_.*', r'\1', os.path.basename(_file)))
            _measured_attribute = re.sub(r'^\d+_(\w+)\.\w+$', r'\1', os.path.basename(_file))
            _filetype = re.sub(r'^\d+_\w+\.(\w+)$', r'\1', os.path.basename(_file))

            _mock_project_folder = "{tmp}/{measure_value}_{attribute}".format(
                tmp=_tmp_base_folder,
                measure_value=_measure_value,
                attribute=_measured_attribute
            )
            if not os.path.exists(_mock_project_folder):
                os.mkdir(_mock_project_folder)

            self._measures['doc_words'] = self._measures['doc_words'] + _measure_value
            if self._measures['readme_words'] < _measure_value:
                self._readme_folder = _mock_project_folder
                self._measures['readme_words'] = _measure_value


            # We copy the mock file to the test area.
            # The copy is named as it would be in a real project.
            copy(_file, _mock_project_folder+"/README."+_filetype)

        self._tmp_base_folder = _tmp_base_folder
        self._docs_measures_dict = _docs_measures_dict


    def test_doc_size(self):
        """ We want a function, that returns the word count of the for all possible doc files. """

        _doc_size = project_doc_size(self._tmp_base_folder)

        self.assertEqual(
            int(self._measures['doc_words']),
            _doc_size
        )

    def test_main_readme_size(self):
        """ We want a function, that returns the word count of the root README.

        It should not measure readme files in subfolders.
        The main, that explains the project should be at the root of it.
        """

        _readme_size = project_readme_size(self._readme_folder)

        self.assertEqual(
            int(self._measures['readme_words']),
            _readme_size
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
        """ See if we get expected comment density.

        Copy all test files into the test area,
        let them get measured and check against expected values.
        """
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

    def test_average_standard_compliance(self):
        """ See if we get expected standard compliance measures.

        Create test project inside the tmp folder.
        Fill it with mock python files.
        Measure the test project and compare to expected values.
        """

        with open(self._tmp_base_folder+"/half.py", 'w') as half_compliant_file:
            half_compliant_file.write('# Not a Docstring')
            half_compliant_file.write('\n')
            half_compliant_file.write('import os # Bad Inline Comment\n')

        _half_compliant_test = standard_compliance(
            self._tmp_base_folder
        )
        self.assertEqual(float(0.5), _half_compliant_test)

        with open(self._tmp_base_folder+"/full.py", 'w') as compliant_file:
            compliant_file.write('"""DOCSTRING"""')
            compliant_file.write('\n')
            compliant_file.write('import os\n')

        # The 0.5 and 1.0 compliance file should average together to 0.75
        _half_plus_full_avg_compliant_test = standard_compliance(
            self._tmp_base_folder
        )
        self.assertEqual(float(0.75), _half_plus_full_avg_compliant_test)

    def tearDown(self):
        """ Clean Up """
        rmtree(self._tmp_base_folder)
        # pkg_resources.resources_filename cashes files, when
        # in a compiled distribution. We need to clean up potentially
        # created files.
        pkg_resources.cleanup_resources()

class TestInstallability(unittest.TestCase):
    """ Test the functions for the installability metrics. """

    def setUp(self):
        """ Create a copy of this package to use it as test data. """
        _this_package = pkg_resources.resource_filename('recoda', '')
        self.test_sandbox = tempfile.mkdtemp()
        self.import_list = pipreqs.get_all_imports(path=_this_package)
        copytree(_this_package, self.test_sandbox+'/recoda')

    def test_requirements_from_requirements_file(self):
        """ Do we get a score when requirements are declared in the requirements.txt"""

        # Test all requirements correctly declared
        with open(
                '{}/{}'.format(self.test_sandbox, 'requirements.txt'),
                'w'
        ) as requirements_mock_file:
            requirements_mock_file.write('\n'.join(self.import_list))

        # All requirements declared should yield 100% i.e. 1
        self.assertEqual(
            1,
            requirements_declared(self.test_sandbox)
        )

        # Test requirements file with one missing dependency
        with open(
                '{}/{}'.format(self.test_sandbox, 'requirements.txt'), 'w'
        ) as requirements_mock_file:
            requirements_mock_file.write('\n'.join(self.import_list[1:]))

        _percentage_of_requirements_declared = (
            float(len(self.import_list) -1) / float(len(self.import_list))
        )
        self.assertEqual(
            _percentage_of_requirements_declared,
            requirements_declared(self.test_sandbox)
        )

    def test_requirements_from_setup_script(self):
        """ Do we get expected behavior, if requirements are in the setup.py

        There can be either no requirements.txt file or a file containing only a "."
        character. We test for both setups.
        """
        _full_path = '{dirname}/{filename}'

        _setup_mock_content = (
            "from distutils.core import setup\n"
            "setup(\n"
            "    name='stub',\n"
            "    install_requires=[\n"
            "        {requirements}\n"
            "    ]\n"
            ")"
        )

        _quoted_import_list = ["\""+item+"\"" for item in self.import_list[1:]]
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

        _percentage_of_requirements_declared = (
            float(len(self.import_list) -1) / float(len(self.import_list))
        )
        self.assertEqual(
            _percentage_of_requirements_declared,
            requirements_declared(self.test_sandbox)
        )

    def test_docker_setup_exists(self):
        """ Can we docker recognize setup correctly? """
        self.assertFalse(
            docker_setup(project_path=self.test_sandbox)
        )

        # Does it work with a Dockerfile?
        _docker_file_path = self.test_sandbox+'/Dockerfile'
        with open(_docker_file_path, 'w') as dockerfile:
            dockerfile.write('FROM python')

        self.assertTrue(
            docker_setup(project_path=self.test_sandbox)
        )

        # Does it work with a docker compose files?
        os.remove(_docker_file_path)
        with open(
                self.test_sandbox+'/docker-compose.yml',
                'w'
            ) as compose_file:
            compose_file.write('version: 3')

        self.assertTrue(
            docker_setup(project_path=self.test_sandbox)
        )

    def test_singularity_setup_exists(self):
        """ Can we docker recognize setup correctly? """
        self.assertFalse(
            singularity_setup(project_path=self.test_sandbox)
        )

        # Does it work with a Dockerfile?
        _singularity_file_path = self.test_sandbox+'/Singularity'
        with open(_singularity_file_path, 'w') as singularity_file:
            singularity_file.write('Bootstrap: docker')
            singularity_file.write('From: python')

        self.assertTrue(
            singularity_setup(project_path=self.test_sandbox)
        )

        # Does it work with a docker compose files?
        os.remove(_singularity_file_path)
        with open(self.test_sandbox+'/Singularity.v1', 'w') as singularity_file:
            singularity_file.write('Bootstrap: docker')
            singularity_file.write('From: python')

        self.assertTrue(
            singularity_setup(project_path=self.test_sandbox)
        )

    def test_packageability(self):
        """ Can we determine if a setup.py file is present? """
        # There is no setup.py file yet.
        self.assertFalse(packageability(self.test_sandbox))

        copy(
            self.test_sandbox+'/recoda/tests/data/mock_setup_py/setup_py',
            self.test_sandbox+'/setup.py'
            )

        self.assertTrue(packageability(self.test_sandbox))



    def tearDown(self):
        """ Clean up the sandbox. """
        rmtree(self.test_sandbox, ignore_errors=True)
        # pkg_resources.resources_filename cashes files, when
        # in a compiled distribution. We need to clean up potentially
        # created files.
        pkg_resources.cleanup_resources()

class TestOpenness(unittest.TestCase):
    """ Test the metric concerned with the licensing of projects """

    _MOCK_LICENSES_DIR = pkg_resources.resource_filename(
        'recoda.tests.data',
        'mock_licenses')

    def setUp(self):
        """ Set up a temp folder to act as test project. """
        self._test_sandbox = tempfile.mkdtemp()

    def test_license_type(self):
        """ See if we can recognize open license files """

        for _original_file in os.listdir(self._MOCK_LICENSES_DIR):
            # The license type is in each files name
            _expected_license = _original_file
            _original_file_path = self._MOCK_LICENSES_DIR+'/'+_original_file
            _file = copy(_original_file_path, self._test_sandbox+'/LICENSE')
            _measured_license = license_type(project_path=self._test_sandbox)

            self.assertEqual(_expected_license, _measured_license)
            os.remove(_file)

        # Test for project without license file.
        _measured_license = license_type(project_path=self._test_sandbox)
        self.assertIsNone(_measured_license)


    def tearDown(self):
        """ Clean up the sandbox. """
        rmtree(self._test_sandbox, ignore_errors=True)
        # pkg_resources.resources_filename cashes files, when
        # in a compiled distribution. We need to clean up potentially
        # created files.
        pkg_resources.cleanup_resources()

class TestVerifiability(unittest.TestCase):
    """ Test the measures for Verifiability."""

    _PATH_TO_THIS_TEST_SCRIPT = pkg_resources.resource_filename(
        'recoda.tests.analyse.python',
        'test_metrics.py')

    def setUp(self):
        """ Set up a temp folder to act as test project. """
        self._test_sandbox = tempfile.mkdtemp()

    def test_existing_test(self):
        """ Do we get a True if there is a test script? """
        copy(
            self._PATH_TO_THIS_TEST_SCRIPT,
            self._test_sandbox+'/test_file.py'
        )
        self.assertTrue(testlibrary_usage(self._test_sandbox))

    def test_nonexisting_test(self):
        """ Do we get false without test scripts? """
        with open(self._test_sandbox+'/non_test_file.py', 'w') as _file:
            _file.write('import os\n')
            _file.write('# Should we do something with unittest\n')
            _file.write('os.path.dirname(os.path.abspath(__file__))\n')

        self.assertFalse(testlibrary_usage(self._test_sandbox))

    def tearDown(self):
        """ Clean up the sandbox. """
        rmtree(self._test_sandbox, ignore_errors=True)
        # pkg_resources.resources_filename cashes files, when
        # in a compiled distribution. We need to clean up potentially
        # created files.
        pkg_resources.cleanup_resources()

class TestCorrectness(unittest.TestCase):
    """ Test the functions measuring the correctness of code. """

    def setUp(self):
        """ Set up mock project with documentation. """
        self._tmp_base_folder = tempfile.mkdtemp()

    def test_error_density(self):
        """ See if we get expected error density measures.

        Create test project inside the tmp folder.
        Fill it with mock python files.
        Measure the test project and compare to expected values.
        """

        with open(self._tmp_base_folder+"/half.py", 'w') as half_dense_file:
            half_dense_file.write('# Not a Docstring')
            half_dense_file.write('\n')
            half_dense_file.write('return\n')

        _half_error_dense_test = error_density(
            self._tmp_base_folder
        )
        self.assertEqual(float(0.5), _half_error_dense_test)

        with open(self._tmp_base_folder+"/none.py", 'w') as no_error_file:
            no_error_file.write('"""DOCSTRING"""')
            no_error_file.write('\n')
            no_error_file.write('VALUE = 1\n')

        # The 0.5 and 1.0 compliance file should average together to 0.75
        _half_plus_no_error_test = error_density(
            self._tmp_base_folder
        )
        self.assertEqual(float(0.75), _half_plus_no_error_test)


    def tearDown(self):
        """ Clean Up """
        rmtree(self._tmp_base_folder)
        # pkg_resources.resources_filename cashes files, when
        # in a compiled distribution. We need to clean up potentially
        # created files.
        pkg_resources.cleanup_resources()
