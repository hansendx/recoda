""" All metrics measuring th installability subfactor. """

import os

import pyroma
import numpy

from recoda.analyse.helpers import (
    search_filename
)

def packageability(project_path: str) -> int:
    """ Gives a score on the packageability of a python software project.

    :param project: Represents a software Project somewhere in local storage.
    """
    _setup_files = _get_setup_location(project_path)

    if len(_setup_files) == 1:
        return pyroma.run('directory', project_path)
    if not _setup_files:
        # No setup.py gets a zero score
        return 0

    _score_list = []
    for _setup_file in _setup_files:
        _score_list.append(
            pyroma.run('directory', project_path)
        )
    return numpy.mean(_score_list)

def _get_setup_location(path: str) -> str:
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
