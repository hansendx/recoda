""" All metrics functions measuring the understandability subfactor. """

import re

from recoda.analyse.helpers import (
    search_filename
)

def project_readme_size(project_path: str) -> int:
    """ Searches for standard doc files and measures their size. """
    # TODO Ignore case?
    _doc_files_suffixes = ['md', 'rst']
    _doc_files = list()

    for _suffix in _doc_files_suffixes:
        _doc_files.extend(
            search_filename(
                base_folder=project_path,
                file_name="README."+_suffix,
                recursive_flag=False
            )
        )

    if len(_doc_files) == 0:
        return 0

    if len(_doc_files) > 1:
        _doc_file = [_path for _path in _doc_files if '.md' in _path][0]
    elif len(_doc_files) == 1:
        _doc_file = _doc_files[0]

    _words = 0

    with open(_doc_file, 'r') as readme_file:
        _readme_string = readme_file.read()
        _words = len(re.split(r'\s', _readme_string))

    return _words
