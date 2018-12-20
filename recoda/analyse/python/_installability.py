""" All metrics measuring th installability subfactor. """

import ast
import os
import re
import tempfile
from typing import Union

from setuptools import find_namespace_packages

import astroid
from pipreqs import pipreqs
from recoda.analyse.helpers import search_filename


def packageability(project_path: str) -> int:
    """ Gives a judgement on potential packageability.

    Searches through a python project for setup files with a 
    call to setup().
    If at least one such setup.p file exists,
    the package is judged to be potentially packageable.

    :param project: Represents a software Project somewhere in local storage.
    :returns:       Projects potential packageability.
    """
    _setup_file_folders = _get_setup_locations(project_path)

    _packageable_setup_files = []
    for _folder in _setup_file_folders:
        _file = _folder+'/setup.py'
        if os.path.isfile(_file):
            _setup_file = open(_file, 'r', encoding='utf-8', errors='replace')
        else:
            continue
        _setup_file_content = _setup_file.read()
        try:
            _setup_node = astroid.parse(_setup_file_content)
        except astroid.exceptions.AstroidSyntaxError:
            return None
        if _astroid_setup_search(_setup_node):
            _packageable_setup_files.append(1)
        elif _regex_setup_search(_setup_file_content):
            _packageable_setup_files.append(1)
        else:
            _packageable_setup_files.append(0)

        # Clean up
        _setup_file_content = None
        _setup_file.close()

    if not _packageable_setup_files:
        return 0

    if 1 in _packageable_setup_files:
        return True
    else:
        return False


def requirements_declared(project_path: str) -> Union[float, str]:
    """ Calculates percentage of not declared dependencies. """
    _declared_requirements = _get_requirements_from_file(path=project_path)
    _setup_requirements = _get_requirements_from_setup(path=project_path)
    try:
        _implied_dependencies = pipreqs.get_pkg_names(
            pipreqs.get_all_imports(
                path=project_path,
                encoding='ISO-8859-1',
                
            )
        )
    except (IndentationError, SyntaxError, ValueError):
        return None
    
    # We cannot calculate a percentage for declared dependencies,
    # if there are no dependencies through imports.
    if not _implied_dependencies:
        return None
    if (not _declared_requirements) and (_setup_requirements is None):
        return "Error"
    if _setup_requirements is None:
        # If this is None,
        # there was a problem parsing the setup file.
        # This is handled in the if statement above.
        # If we still calculate further, this needs
        # to be iterable since we make an "in" comparison with it.
        _setup_requirements = []

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
    _requirements = list()
    _error = False
    for _setup_file in _setup_files:
        _parsed_requirements = _astroid_parse_setup(_setup_file)
        if _parsed_requirements is None:
            _error = True
        if _parsed_requirements:
            _requirements = _requirements + _parsed_requirements

    if not _parsed_requirements and _error:
        return None


    return _requirements

def _get_implied_dependencies(path: str) -> list:
    """ Attempt to replace _get_requirements_from_file

    Extracts import statements via regex.
    Does not catch all import statements and its
    use was rolled back.
    Might still be overhauled and integrated again. 
    """
    _python_files = search_filename(
        base_folder=path,
        file_name="**/*.py",
        recursive_flag=True
    )

    _tmp_project_path = tempfile.mkdtemp()
    _tmp_file_path = _tmp_project_path + "/dependencies.py"
    _tmp_file = open(_tmp_file_path, 'w')
    for file in _python_files:
        for _import in _get_imports(file):
            _tmp_file.write(_import.strip()+'\n')
    _tmp_file.close()

    try:
        _all_imports = pipreqs.get_all_imports(
            path=_tmp_project_path,
            encoding='utf-8'
        )
    except (IndentationError, SyntaxError):
        return None


    # Clean up tmp folder
    if os.path.isfile(_tmp_file_path):
        os.remove(_tmp_file_path)
    if os.path.isdir(_tmp_project_path):
        os.rmdir(_tmp_project_path)

    _imports = _remove_local_dependencies(path, _all_imports)

    return pipreqs.get_pkg_names(_imports)

def _remove_local_dependencies(path:str, _all_imports):

    _local_imports = find_namespace_packages(where=path)

    _cleaned_imports = list()

    for _import in _all_imports:
        if _import not in _local_imports:
            _cleaned_imports.append(_import)

    _all_imports = None
        
    return _cleaned_imports

def _get_imports(file_path: str) -> list:
    """ Parse all import statements form a file. """
    _import_regex = r'(?m)^\s*((?:from\s+\S+\s+){0,1}import\s+(?:(?:(?:[\w\d_-])+(?:[\s,])*)|(?:\s*\([\s,#\w\d_-]*\))|(?:\s*[\s,#\w\d_-]*?)))\s*(?:#.*){0,1}$'

    if os.path.isfile(file_path):
        _file = open(file_path, 'r', errors='replace')
    else:
        return []
    _file_string = _file.read()
    _file.close()
    _file_string = re.sub(r'#.*?\n', '\n', _file_string)
    _file_string = re.sub(r'(?m)"""[\s\S]*?"""', '', _file_string)
    _file_string = re.sub(r'(?m)\'\'\'[\s\S]*?\'\'\'', '', _file_string)

    _import_matches = re.findall(_import_regex, _file_string)

    return _import_matches


def _astroid_parse_setup(path: str) -> list:
    """ Extract requirements out of the setup call in a setup.py

    If for som reason several setup calls are present,
    their requirements are concatenated

    :param path: Full path to the location of a setup.py file.
    :returns:    All declared requirements of a setup.py file contained in a string.
    """
    if os.path.isfile(path):
        _setup_file = open(path, 'r', errors='replace')
    else:
        return []
    _setup_content = _setup_file.read()
    _setup_file.close()
    _setup_list = None
    try:
        _setup_list = _astroid_setup_search(
            astroid.parse(_setup_content)
        )
        _setup_content = None
    except (astroid.exceptions.AstroidSyntaxError, AttributeError):
        _setup_content = re.sub(r'#.*?\n', '\n', _setup_content)
        _setup_content = re.sub(r'(?m)"""[\s\S]*?"""', '', _setup_content)
        _setup_content = re.sub(r'(?m)\'\'\'[\s\S]*?\'\'\'', '', _setup_content)

    _requirements_regex = (
        r'.*(?:(?:install_requires)|(?:tests_require))=(\[[\s\S]*?\]).*'
     )

    _requirement_list = list()
    _requirement_strings = list()
    if _setup_list:
        for _setup in _setup_list:
            _requirement_strings.extend(
                re.findall(
                    _requirements_regex,
                    _setup
                )
            )
    elif not _setup_content:
        return None
    else:
        _requirement_strings = re.findall(
            _requirements_regex,
            _setup_content
        )
    for _requirement_string in _requirement_strings:
        try:
            _requirement_list = _requirement_list + ast.literal_eval(_requirement_string)
        except (ValueError, SyntaxError):
            return None

    for _index, _requirement in enumerate(_requirement_list):
        _requirement_list[_index] = re.sub(r'[\s><=].*', '', _requirement)


    return _requirement_list

def _clean_requirements_entries(requirements_list: list) -> list:
    """ Remove version information from a list with requirement strings. """

    _entry_regex = r'^(.*?)/s*[;><=].*$'

    for index, entry in enumerate(requirements_list):
        requirements_list[index] = re.sub(_entry_regex, r'\1', entry)

    return requirements_list

def _regex_setup_search(setup_content: str) -> list:
    """ Fallback for _astroid_setup_search.

    May only match parts of the setup call.
    Should not be used if full call is needed. 
    """
    # Remove matching error factors
    setup_content = re.sub(r'#.*?\n', '\n', setup_content)
    setup_content = re.sub(r'(?m)"""[\s\S]*?"""', '', setup_content)
    setup_content = re.sub(r'(?m)\'\'\'[\s\S]*?\'\'\'', '', setup_content)


    _setup_regex = r'.*(setup\([\s\S]*?\)).*'

    return re.findall(_setup_regex, setup_content)


def _astroid_setup_search(node: astroid.nodes) -> list:
    """ Search for the setup function calls in a astroid tree recursively.

    :param node: A astroid node object containing a setup.py parsetree or parts of it.  
    :returns:    A list of strings containing a setup call each.
    """

    _setup_call_list = list()
    for child in node.get_children(): 
        if child.as_string()[:6] == 'setup(':
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
