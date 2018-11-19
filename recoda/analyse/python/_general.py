""" General metrics potentially used for calculating several quality aspects. """
import os
import re
from recoda.analyse.python.helpers import get_python_files

def count_loc(project_path: str) -> int:
    """ Count the lines of python code in a project.

    A LOC is a line, that is not blank,
    meaning that comments are also part of LOC here.
    """
    _python_files = get_python_files(project_path)

    _loc = 0

    for _file_path in _python_files:
        if os.path.isfile(_file_path):
            _loc = _loc + _single_file_loc(_file_path)

    return _loc

def _single_file_loc(file_path: str) -> int:
    """ Count LOC for one file. """
    _loc = 0
    _file = open(file_path, 'r', errors='ignore')
    for line in _file:
        if not re.match(r'^\s*$', line):
            _loc = _loc + 1

    return _loc

