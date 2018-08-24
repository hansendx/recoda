""" All metrics functions measuring the understandability subfactor. """

import os
import re
from textstat.textstat import textstat

from recoda.analyse.helpers import (
    search_filename,
    strip_text_from_md,
    strip_text_from_rst
)

def project_readme_size(project_path: str) -> int:
    """ Searches for standard doc files and measures their size. """

    _doc_file = _get_main_readme(project_path)

    if not _doc_file:
        return 0

    _words = 0

    try:
        _readme_string = _strip_text(_doc_file)
        _words = len(re.split(r'\s', _readme_string))
    except:
        return 0

    return _words

def flesch_reading_ease(project_path: str) -> int:
    """ Calculates reading ease with textstat. """
    # Error rate in sillable
    _doc_file = _get_main_readme(project_path)

    try:
        _readme_string = _strip_text(_doc_file)
        return textstat.flesch_reading_ease(_readme_string)
    except:
        return 0

def flesch_kincaid_grade(project_path: str) -> int:
    """ Calculates readinch kincaid reading grade with textstat. """
    # Error rate in sillable
    _doc_file = _get_main_readme(project_path)

    try:
        _readme_string = _strip_text(_doc_file)
        return textstat.flesch_kincaid_grade(_readme_string)
    except:
        return 0



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
        # If we find several README files with different suffix, we expect them to
        # be redundant and only take the markdown file.
        _doc_file = [_path for _path in _doc_files if '.md' in _path.lower()][0]
        if not _doc_file:
            # If two rst README files are present, we take one of them.
            _doc_file = [_path for _path in _doc_files if '.rst' in _path.lower()][0]
    elif len(_doc_files) == 1:
        _doc_file = _doc_files[0]


    return _doc_file

def _strip_text(_doc_file: str) -> str:
    """ Determines filetype of Docfile and calls the strip function to call.

    :returns: Input text without the markup parts.
    """
    # Easy way to ignore the case of the original suffix.
    _file_name_lowercased = os.path.basename(_doc_file).lower()

    _doc_string = ''
    with open(_doc_file, 'r') as file:
        if '.md' in _file_name_lowercased:
            _doc_string = strip_text_from_md(file.read())
        elif '.rst' in _file_name_lowercased:
            _doc_string = strip_text_from_md(file.read())

    return _doc_string
