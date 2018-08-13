""" Provides functionality to calculate software metrics in python projects.
"""

import os
from typing import Union
import git

def packageable(project: Union[str, git.repo.base.Repo]) -> int:
    """ Gives a score on the packageability of a python software project.

    :param project: Represents a software Project somewhere in local storage.
    :raises NotADirectoryError: When project directory does not exist.
    """

    #_path = _get_project_directory(project)
    #_setup_dir = _get_setup_location(_path)
    return 0

def _get_setup_location(path: str) -> str:
    """ Returns a list of paths to setup.py files in a directory.
    """
    #TODO
    return ''


