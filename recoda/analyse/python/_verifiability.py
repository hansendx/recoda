""" Measures that try to show how easy it is to verify a projects function.

"""

import re

from recoda.analyse.helpers import search_filename

PYTHON_TEST_LIBRARIES = (
    # Unit testing
    'unittest',
    'doctest',
    'pytest',
    'testify',
    'zope.testing',
    'sancho',
    # Mocking libraries
    'ludibrio',
    'mock',
    'pymock',
    'pmock',
    'minimock',
    'svnmock',
    'mocker',
    'reahl.stubble',
    'mocktest',
    'fudge',
    'mockito',
    'flexmock',
    'doublex',
    'aspectlib',
    # Fuzz testing
    'hypothesis',
    'antiparser',
    'twill',
    'webunit',
    'zope.testbrowser',
    'webtest',
    'PAM30',
    # Acceptance testing
    'behave',
    'lettuce',
)

def testlibrary_usage(project_path: str) -> bool:
    """ Check for the import of Test Libraries.

    Searches for the import of a test library inside the projects
    python-script files.
    A project is judged as using tests if one of the test libraries
    in PYTHON_TEST_LIBRARIES is imported.

    :param project_path:    Root path to the Project to be measured.
    :returns:               True if a test library imported at least once.

    """
    _python_script_files = search_filename(
        base_folder=project_path,
        file_name='*.py'
    )

    for _file_path in _python_script_files:
        _test_exists = _find_testlibrary_import(file_path=_file_path)
        if _test_exists:
            return True

    return False

def _find_testlibrary_import(file_path: str) -> bool:
    """ Search a single file for the import of a test library. """
    # Multiprocessing gobbled up a lot of memory using with blocks.
    # So we handle files here directly.
    _file_handler = open(file_path, 'r')

    _grouped_library_strings = ["(?:"+ lib +")" for lib in PYTHON_TEST_LIBRARIES]

    _import_regex = re.compile(
        r'^\s*(?:(?:from)|(?:import)).*(?:' +
        '|'.join(_grouped_library_strings) +
        ')'
    )


    for _line in _file_handler:
        _match = re.match(_import_regex, _line)
        if _match:
            _file_handler.close()
            return True

    _file_handler.close()
    return False
