""" All metrics measuring th installability subfactor. """

import os
import re
import sys

import pipreqs.pipreqs as pipreqs
import pyroma
import numpy

from recoda.analyse.helpers import (
    search_filename
)

def packageability(project_path: str) -> int:
    """ Gives a score on the packageability of a python software project.

    :param project: Represents a software Project somewhere in local storage.
    """
    _setup_files = _get_setup_locations(project_path)

    if len(_setup_files) == 1:
        _stdout = sys.stdout
        sys.stdout = open('/dev/null', 'w')
        _score = pyroma.run('directory', project_path)
        sys.stdout = _stdout
        return _score
    if not _setup_files:
        # No setup.py gets a zero score
        return 0

    _score_list = []
    for _setup_file in _setup_files:
        _score_list.append(
            pyroma.run('directory', project_path)
        )
    return numpy.mean(_score_list)

def requirements_declared(project_path: str) -> bool:
    """ Checks, if requirements are declared for imports. """
    _declared_requirements = _get_requirements_content(path=project_path)
    _implied_requirements = pipreqs.get_all_imports(path=project_path)

    for requirement in _implied_requirements:
        if requirement not in _declared_requirements:
            return False
    return True

def _get_requirements_content(path: str) -> set:
    """ Returns a list of paths to requirement files in a directory.

    :returns: The result of a call to search_filename
              of the recoda.analyse.helpers module
              with path as value for base_folder
              and "requirements.txt" as file to search.
    """
    _file_string = 'requirements.txt'
    _file_list = search_filename(
        base_folder=path,
        file_name=_file_string
    )
    _requirements_content = set()

    for file_name in _file_list:
        for requirement in pipreqs.parse_requirements(file_=file_name):
            _requirements_content.add(requirement['name'])
    
    return _requirements_content




def _get_setup_locations(path: str) -> str:
    """ Returns a list of paths to setup.py files in a directory.

    :returns: The result of a call to search_filename
            of the recoda.analyse.helpers module
            with path as base_folder and "setup.py"
            as file to search.
    """
    _setup_file_string = 'setup.py'
    _setup_file_list = search_filename(
        base_folder=path,
        file_name=_setup_file_string
    )

    return [os.path.dirname(_path) for _path in _setup_file_list]
