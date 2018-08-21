""" All metrics functions measuring the understandability subfactor. """

import re
from textstat.textstat import textstat

from recoda.analyse.helpers import (
    search_filename
)

def project_readme_size(project_path: str) -> int:
    """ Searches for standard doc files and measures their size. """

    _doc_file = _get_main_readme(project_path)

    if not _doc_file:
        return 0

    _words = 0

    with open(_doc_file, 'r') as readme_file:
        _readme_string = readme_file.read()
        _words = len(re.split(r'\s', _readme_string))

    return _words
    
def flesch_reading_ease(project_path:str) -> int:
    """ Calculates reading ease with textstat. """
    _doc_file = _get_main_readme(project_path)

    with open(_doc_file, "r") as readme_file:
        return textstat.flesch_reading_ease(readme_file.read())


def _get_main_readme(project_path: str) -> str:
    """ Searches for a projects main README file in the projects base. """
    _doc_files_suffixes = ['[Mm][Dd]', '[Rr][Ss][Tt], ']
    _doc_files = list()

    for _suffix in _doc_files_suffixes:
        _doc_files.extend(
            search_filename(
                base_folder=project_path,
                file_name="[Rr][Ee][Aa][Dd][Mm][Ee]."+_suffix,
                recursive_flag=False
            )
        )

    if not _doc_files:
        return ""

    if len(_doc_files) > 1:
        _doc_file = [_path for _path in _doc_files if '.md' in _path.lower()][0]
        if not _doc_file:
            _doc_file = [_path for _path in _doc_files if '.rst' in _path.lower()][0]
    elif len(_doc_files) == 1:
        _doc_file = _doc_files[0]
    
    return _doc_file