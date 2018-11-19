""" All metrics measuring th installability subfactor. """

import os
import re
import warnings

import astroid
import numpy
from pipreqs import pipreqs
from recoda.analyse.helpers import search_filename


def packageability(project_path: str) -> int:
    """ Gives a score on the packageability of a python software project.

    The score is the percentage of setup scripts, that contain a call to setup.

    :param project: Represents a software Project somewhere in local storage.
    :returns:       A score on a projects packageability.
    """
    _setup_files = _get_setup_locations(project_path)

    _packageable_setup_files = []
    for _file in _setup_files:
        if os.path.isfile(_file):
            _setup_file = open(_file+'/setup.py', 'r', encoding='utf-8', errors='replace')
        else:
            continue

        try:
            _setup_node = astroid.parse(_setup_file.read())
        except astroid.exceptions.AstroidSyntaxError:
            return None
        if _astroid_setup_search(_setup_node):
            _packageable_setup_files.append(1)
        else:
            _packageable_setup_files.append(0)
        _setup_file.close()

    if not _packageable_setup_files:
        return float(0)

    with warnings.catch_warnings():
        # This spams warnings when there is nothing to measure i.e.
        # When we only have None to calculate a mean.
        # A list only containing None values is expected and
        # the warning superfluous.
        warnings.simplefilter("ignore", category=RuntimeWarning)
        return numpy.nanmean(_packageable_setup_files)

def requirements_declared(project_path: str) -> float:
    """ Calculates percentage of not declared dependencies. """
    _declared_requirements = _get_requirements_from_file(path=project_path)
    _setup_requirements = _get_requirements_from_setup(path=project_path)
    try:
        _implied_dependencies = (
            pipreqs.get_all_imports(
                path=project_path,
                encoding='utf-8'
            )
        )
    except (SyntaxError, IOError, ValueError):
        return None
    # We cannot calculate a percentage for declared dependencies,
    # if there are no dependencies through imports.
    if not _implied_dependencies:
        return None

    _correctly_declared_requirements_count = len(_implied_dependencies)
    for requirement in _implied_dependencies:
        if requirement not in _declared_requirements and requirement not in _setup_requirements:
            _correctly_declared_requirements_count = _correctly_declared_requirements_count - 1

    return float(_correctly_declared_requirements_count) / len(_implied_dependencies)

def docker_setup(project_path: str) -> bool:
    """ Tries to find evidence of a docker setup in the project. """
    _file_names = ['[Dd]ockerfile', '[Dd]ocker-compose.yml']

    for name in _file_names:
        _findings = search_filename(
            base_folder=project_path,
            file_name=name,
            recursive_flag=True
        )
        if _findings:
            return True

    return False

def singularity_setup(project_path: str) -> bool:
    """ Tries to find evidence of a singularity setup in the project. """
    _file_names = ['[Ss]ingularity.*', '[Ss]ingularity']

    for name in _file_names:
        _findings = search_filename(
            base_folder=project_path,
            file_name=name,
            recursive_flag=True
        )
        if _findings:
            return True

    return False

def _get_requirements_from_file(path: str) -> set:
    """ Returns a list of requirements parsed from all requirements files insode a path.

    :param path: Full path to a python software project.
    :returns:    A set of all requirements found in requirements.txt files.
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

def _get_requirements_from_setup(path: str) -> str:
    """ Extract requirements declared in the setup.py files of a project.

    If several setup.py files are contained in a project,
    their declared requirements are concatenated.

    :param path: Full path to the location of a python software project.
    :returns:    All declared requirements of a project contained in a string.
    """
    _setup_file_locations = _get_setup_locations(path)
    if not _setup_file_locations:
        return ''
    _setup_files = [path+'/setup.py' for path in _setup_file_locations]
    _requirements = ""
    for _setup_file in _setup_files:
        _parsed_requirements = _astroid_parse_setup(_setup_file)
        if _parsed_requirements:
            _requirements = _requirements + _parsed_requirements

    return _requirements

def _astroid_parse_setup(path: str) -> str:
    """ Extract requirements out of the setup call in a setup.py

    If for som reason several setup calls are present,
    their requirements are concatenated

    :param path: Full path to the location of a setup.py file.
    :returns:    All declared requirements of a setup.py file contained in a string.
    """
    _setup_file = open(path)
    _setup_content = _setup_file.read()
    _setup_file.close()
    try:
        _setup_parse_tree = astroid.parse(_setup_content)
    except astroid.exceptions.AstroidSyntaxError:
        return None
    _requirements_regex = r'.*install_requires=\[(.*?)\].*'
    _requirement_string = ''
    for _setup in _astroid_setup_search(_setup_parse_tree): 
        _requirement_string = _requirement_string + re.sub(
            _requirements_regex, r'\1',
            _setup
        )
    return _requirement_string

def _astroid_setup_search(node: astroid.nodes) -> list:
    """ Search for the setup function calls in a astroid tree recursively.

    :param node: A astroid node object containing a setup.py parsetree or parts of it.  
    :returns:    A list of strings containing a setup call each.
    """

    _setup_call_list = list()
    for child in node.get_children(): 
        if child.as_string()[:5] == 'setup':
            _setup_call_list.append(child.as_string())
        else:
            _setup_call_list = _setup_call_list + _astroid_setup_search(child)

    return _setup_call_list

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
