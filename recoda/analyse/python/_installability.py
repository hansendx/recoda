""" All metrics measuring th installability subfactor. """

import os
import re
import sys

import astroid
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

def requirements_declared(project_path: str) -> float:
    """ Checks, if requirements are declared for imports. """
    _declared_requirements = _get_requirements_txt_requirements(path=project_path)
    _setup_requirements = _get_setup_requirements(path=project_path)
    _implied_requirements = pipreqs.get_all_imports(path=project_path)

    _correctly_declared_requirements_count = len(_implied_requirements)
    for requirement in _implied_requirements:
        if requirement not in _declared_requirements and requirement not in _setup_requirements:
            _correctly_declared_requirements_count = _correctly_declared_requirements_count - 1
    
    return float(_correctly_declared_requirements_count) / len(_implied_requirements)

def _get_requirements_txt_requirements(path: str) -> set:
    """ Returns a list of requirements parsed from all requirements files insode a path.

    :returns: A set of all requirements found.
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

def _get_setup_requirements(path: str) -> str:
    _setup_file_locations = _get_setup_locations(path)
    if not _setup_file_locations:
        return ''
    _setup_files = [path+'/setup.py' for path in _setup_file_locations]
    _requirements = ""
    for _setup_file in _setup_files:
        _requirements = _requirements + _astroid_parse_for_setup(_setup_file)

    return _requirements

def _astroid_parse_for_setup(path: str) -> set:
    _setup_file = open(path)
    _setup_content = _setup_file.read()
    _setup_file.close()
    _setup_parse_tree = astroid.parse(_setup_content)
    _requirement_string = ''
    for child in _setup_parse_tree.get_children(): 
        if child.as_string()[:5] == 'setup': 
            return re.sub(r'.*install_requires=\[(.*?)\].*', r'\1',  child.as_string())



def _get_setup_locations(path: str) -> list:
    """ Returns a list of paths to setup.py files in a directory.

    :returns: List of paths containing a setup.py file
    """
    _setup_file_string = 'setup.py'
    _setup_file_list = search_filename(
        base_folder=path,
        file_name=_setup_file_string
    )

    return [os.path.dirname(_path) for _path in _setup_file_list]
