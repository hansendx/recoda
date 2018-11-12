""" Measures that concern themselves with the correctness of projects. """

import warnings
from subprocess import PIPE, Popen
from typing import Union

import numpy
from recoda.analyse.python.helpers import get_python_files


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
            return None
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

    _process = Popen(
        [
            'pylint',
            '-s',
            'n',
            '--errors-only',
            "--msg-template='{msg_id}'",
            _file_path
        ],
        stdout=PIPE
    )
    _output = _process.communicate()
    _errors = _parse_pylint_output(_output[0].decode("utf-8"))

    if _errors is None:
        return None

    _file = open(_file_path, 'r')

    _line_number = 0
    for _ in _file.readlines():
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
