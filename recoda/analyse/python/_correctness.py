""" Measures that concern themselves with the correctness of projects. """

import re
import warnings
from io import StringIO
from subprocess import PIPE, Popen
from typing import Union

import numpy
from pyflakes.api import checkPath
from pyflakes.reporter import Reporter
from recoda.analyse.python.helpers import get_python_files

def project_errors(project_path:str) -> int:
    """ Get all errors pylint finds for a project. """
    pass

def error_density(project_path: str) -> float:
    """ Get the average of the error density for every file.

    Count the errors of all python files,
    that can be found with pylint.
    Calculate the error density.
    Then calculate the average for all files.

    :param project_path: Full path to the project to be measured.
    :returns:            Average error density for all script files.
    """
    _python_files = get_python_files(project_path)

    _scores = list()
    for _file_path in _python_files:
        _score = _get_error_density(_file_path)
        if _score is None:
            continue
            #return None
        if _score is not False:
            _scores.append(_score)

    with warnings.catch_warnings():
        # This spams warnings when there is nothing to measure i.e.
        # When we only have None to calculate a mean.
        # A list only containing None values is expected and
        # the warning superfluous.
        warnings.simplefilter("ignore", category=RuntimeWarning)
        return numpy.nanmean(_scores)


def _get_error_density(_file_path: str) -> Union[float, bool]:
    """ Get standard compliance for a singe file. """

    _output_handler = StringIO()
    _error_handler = StringIO()
    _pyflake_reporter = Reporter(_output_handler, _error_handler)


    _check_result = checkPath(_file_path, _pyflake_reporter)

    _error_handler.close()
    _error_handler = None

    _error_string = _output_handler.getvalue()
    # We will just have an empty string 
    # if pyflakes outputs nothing i.e.
    # if we have no errors.
    if _error_string:
        # We use strip to not get empty strings
        # at the start or end
        # when we split the lines on \n.
        _error_lines = _error_string.strip().split('\n')
        _errors = len(_error_lines)
    else:
        _errors = 0

    # Clean up space
    _output_handler.close()
    _output_handler = None
    _error_lines = None
    _pyflake_reporter = None


    if _errors is None:
        return None

    _file = open(_file_path, 'r', encoding='utf-8', errors='ignore')

    _line_number = 0
    for _line in _file.readlines():
        if re.match(r'^\s$', _line):
            continue
        _line_number = _line_number + 1

    _file.close()

    if _line_number == 0:
        return False

    _error_density = float(_errors / _line_number)
    # We have calculated the percentage of non-compliant lines,
    # we want the percentage of the compliant lines.
    return float(1 - _error_density)

def _parse_pylint_output(_pylint_output: str) -> int:
    """ Parse pylint string and count Error messages. """
    _error_count = 0
    # We expect to get a consecutive string with \n between messages
    _message_list = _pylint_output.split('\n')
    for message in _message_list:
        if message == 'E0001' or message.startswith('F'):
            # A python syntax error will block all other errors.
            # It will prevent pylint to even parse the code using ast.
            # A fatal error may also prevent a full analysis.
            # We cannot use this, it would suppress the convention errors,
            # giving this file a perfect score.
            # This could come form a legit error
            # or from py3 incompatibility.
            return None
        if message.startswith('E') and message != 'E0401':
            # Dependencies may not be installed, so we cannot
            # count import errors into our measurement.
            # Checking of correct dependency declaration is also
            # already part of another measure.
            _error_count = _error_count + 1

    return _error_count
