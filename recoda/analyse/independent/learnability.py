""" All metrics functions measuring the understandability subfactor. """

import os
import re
import warnings

import numpy
from recoda.analyse.helpers import (
    search_filename,
    strip_text_from_md,
    strip_text_from_rst
)
from textstat.textstat import textstat


def project_readme_size(project_path: str) -> int:
    """ Searches for standard doc files and measures their size. """

    _doc_file = _get_main_readme(project_path)

    if not _doc_file:
        return 0

    _words = 0

    try:
        _readme_string = _strip_text(_doc_file).strip()
        _words = len(re.split(r'\s', _readme_string))
    except:
        return 0

    return _words

def project_doc_size(project_path: str) -> int:
    """ Searches for standard doc files and measures their size. """

    _doc_files = _get_doc_files(project_path)

    if not _doc_files:
        return 0

    _words = 0

    for _doc_file in _doc_files:
        try:
            _readme_string = _strip_text(_doc_file).strip()
            _words = _words + len(re.split(r'\s', _readme_string))
        except:
            continue

    return _words

def readme_flesch_reading_ease(project_path: str) -> int:
    """ Calls flesch_reading_ease with full_docs = False """
    return flesch_reading_ease(project_path=project_path, full_docs = False)

def readme_flesch_kincaid_grade(project_path: str) -> int:
    """ Calls flesch_kincaid_grade with full_docs = False """
    return flesch_kincaid_grade(project_path=project_path, full_docs = False)


def flesch_reading_ease(project_path: str, full_docs: bool = True) -> int:
    """ Calculates reading ease with textstat.
    
    The true reading ease will possibly be overestimated.
    textstat sillable count is not a 100% accurate.
    This is because lower sillable words are judged as more
    readable and textstat uses Pyphen, which hiphenates
    some words with less hyphens than their true sillable count.
    """
    # Error rate in sillable
    if full_docs:
        _doc_files = _get_doc_files(project_path)
    else:
        _doc_files = [_get_main_readme(project_path)]

    _scores = list()

    if not _doc_files:
        return None

    for _doc_file in _doc_files:
        try:
            _readme_string = _strip_text(_doc_file)
            if not _readme_string:
                continue
            _scores.append(textstat.flesch_reading_ease(_readme_string))
        except:
            continue

    if not _scores:
        return None

    with warnings.catch_warnings():
        # This spams warnings when there is nothing to measure i.e.
        # When we only have None to calculate a mean.
        # A list only containing None values is expected and
        # the warning superfluous.
        warnings.simplefilter("ignore", category=RuntimeWarning)
        return numpy.nanmean(_scores)


def flesch_kincaid_grade(project_path: str, full_docs: bool = True) -> int:
    """ Calculates readinch kincaid reading grade with textstat.
    
    The true grade level will possibly be underestimated.
    textstat sillable count is not a 100% accurate.
    This is because lower sillable words are judged as more
    readable and textstat uses Pyphen, which hiphenates
    some words with less hyphens than their true sillable count.
    """
    # Error rate in sillable
    if full_docs:
        _doc_files = _get_doc_files(project_path)
    else:
        _doc_files = [_get_main_readme(project_path)]
    _scores = list()

    if not _doc_files:
        return None

    for _doc_file in _doc_files:
        try:
            _readme_string = _strip_text(_doc_file)
            if not _readme_string:
                continue
            _scores.append(textstat.flesch_kincaid_grade(_readme_string))
        except:
            continue

    if not _scores:
        return None

    with warnings.catch_warnings():
        # This spams warnings when there is nothing to measure i.e.
        # When we only have None to calculate a mean.
        # A list only containing None values is expected and
        # the warning superfluous.
        warnings.simplefilter("ignore", category=RuntimeWarning)
        return numpy.nanmean(_scores)



def _get_main_readme(project_path: str) -> str:
    """ Searches for a projects main README file in the projects base. """
    _doc_files_suffixes = ['.[Mm][Dd]', '.[Rr][Ss][Tt]', '.[Tt][Xx][Tt]', '']
    _doc_files = list()

    for _suffix in _doc_files_suffixes:
        _doc_files.extend(
            search_filename(
                base_folder=project_path,
                file_name="[Rr][Ee][Aa][Dd][Mm][Ee]"+_suffix,
                recursive_flag=False
            )
        )

    if not _doc_files:
        return ""

    # If we find several README files, we take the biggest in size
    # This will hopefully get us the one with the most effort put in.
    _file_size = -1
    _doc_file = ''
    for _file in _doc_files:
        if os.path.getsize(_file) > _file_size:
            _file_size = os.path.getsize(_file)
            _doc_file = _file


    return _doc_file


def _get_doc_files(project_path: str) -> list:
    """ Searches for a projects main README file in the projects base. """
    _doc_files_suffixes = ['.[Mm][Dd]', '.[Rr][Ss][Tt]' ]
    _readme_files_suffixes = ['.[Tt][Xx][Tt]', '']
    _doc_files = set()

    for _suffix in _doc_files_suffixes:
        _doc_files.update(
            search_filename(
                base_folder=project_path,
                file_name="*"+_suffix,
                recursive_flag=True
            )
        )
    for _suffix in _readme_files_suffixes:
        _doc_files.update(
            search_filename(
                base_folder=project_path,
                file_name="[Rr][Ee][Aa][Dd][Mm][Ee]"+_suffix,
                recursive_flag=True
            )
        )

    if not _doc_files:
        return None

    return _doc_files

def _strip_text(_doc_file: str) -> str:
    """ Determines filetype of Docfile and calls the strip function to call.

    :returns: Input text without the markup parts.
    """
    # Easy way to ignore the case of the original suffix.
    _file_name_lowercased = os.path.basename(_doc_file).lower()

    _doc_string = ''
    if not os.path.isfile(_doc_file):
        return ""

    with open(_doc_file, 'r') as file:
        if re.match(r'^.*\.md$', _file_name_lowercased):
            _doc_string = strip_text_from_md(file.read())
        elif re.match(r'^.*\.rst$', _file_name_lowercased):
            _doc_string = strip_text_from_rst(file.read())
        else:
            _doc_string = file.read()

    return _doc_string
