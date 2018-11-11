""" Helper Functions for python specific measures. """

import os

from recoda.analyse.helpers import search_filename

def get_python_files(project_path: str) -> list:
    """ Returns a list of all python files in a directory and its sub directories. """
    _python_glob = "**/*.py"
    _python_files = search_filename(
        base_folder=project_path,
        file_name=_python_glob,
        recursive_flag=True
    )

    _files = [_file for _file in _python_files if os.path.isfile(_file)]

    return _python_files
