""" Module to contain the measuring tools for code understandability. """

import os
import re
import tokenize
from subprocess import PIPE, Popen

import astroid
import numpy
from recoda.analyse.python.helpers import get_python_files

TIMEOUT = 200

def average_comment_density(project_path) -> float:
    """ Calculate the average comment density for all .py files.

    Commented Lines of Code (CLOC) are:

     * A line with a # Comment.
     * Every line of a Docstring containing Text.

    Multiline string comments are excluded for now.

    Non Commented Lines of Code (NCLOC) exclude:

     * Comments
     * Blank lines

    Lines of Code (LOC) are CLOC + NCLOC.

    :returns:   The average comment density of all .py files.
                With comment density for one file defined as CLOC/LOC.
    """

    _file_paths = get_python_files(project_path)

    _comment_density_scores = []
    for _file_path in _file_paths:
        _comment_density_scores.append(_get_comment_density(_file_path))

    _comment_density_scores_cleaned = [
        _value
        for _value in _comment_density_scores
        if _value is not None
    ]

    _group_size = float(len(_comment_density_scores_cleaned))
    _sum_scores = sum(_comment_density_scores_cleaned)

    if _group_size:
        return float(_sum_scores / _group_size)
    return None

def average_standard_compliance(project_path: str) -> float:
    """ Get the average of the standard compliance density for every file.

    Count the style offences of all python files
    and normalize it using the files size.
    Then calculate the average for all files.

    :param project_path: Full path to the project to be measured.
    :returns:            Average standard compliance of all files
    """
    _python_files = get_python_files(project_path)

    _scores = list()
    for _file_path in _python_files:
        _score = _get_standard_compliance(_file_path)
        if _score is None:
            return None
        _scores.append(_score)

    return numpy.mean(_scores)


def _get_standard_compliance(_file_path: str) -> float:
    """ Get standard compliance for a singe file. """

    _line_number = 0
    _file = open(_file_path, 'r')

    for _ in _file.readlines():
        _line_number = _line_number + 1

    _file.close()

    _process = Popen(
        [
            'pylint',
            '-s',
            'n',
            '--disable=all',
            '--enable=C',
            '--enable=F',
            '--enable=E0001',
            "--msg-template='{C}'",
            _file_path
        ],
        stdout=PIPE
    )
    _output = _process.communicate()
    _score = _parse_pylint_output(_output[0].decode("utf-8"))

    if _score is None:
        return None

    _non_compliance = float(_score / _line_number)
    # We have calculated the percentage of non-compliant lines,
    # we want the percentage of the compliant lines.
    return float(1 - _non_compliance)

def _parse_pylint_output(_pylint_output: str) -> int:
    """ Parse pylint string and count Convention messages. """
    _convention_error = 0
    # We expect to get a consecutive string with \n between messages
    _message_list = _pylint_output.split('\n')
    for message in _message_list:
        if message == 'E' or message == 'F':
            # A python syntax error will block all other errors.
            # We cannot use this, it would suppress the convention errors,
            # giving this file a perfect score.
            # This could come form a legit error
            # or from py3 incompatibility.
            return None
        _convention_error = _convention_error + 1

    return _convention_error



def _get_comment_density(_file_path):
    """ Get the comment density for a single file. """

    # All the counting variables.
    _single_comments = _multiline_comments = _lines_of_code = 0

    # We cannot count what does not exist.
    # This is expected to be faulty input, so we cannot return 0,
    # since this would influence the average.
    if not os.path.isfile(_file_path):
        return None

    # Characters, that cannot be recognized do not change line counts (hopefully)
    # and the actual text is not important for this measure.
    # We let open replace those characters because we do not want it to cause
    # the measurement run to exit on the error.
    _file_content = open(_file_path, 'r', errors='replace')
    _file_string = ''

    # We read the file this way to count all non blank lines of code.
    # Parts of multiline strings, containing only whitespace characters
    # or string delimiter (""") will also be counted as blank lines.
    for line in _file_content:
        if not re.match(r'^\s*("""){0,1}\s*$', line):
            _lines_of_code = _lines_of_code + 1
        _file_string = _file_string + line
    _file_content.close()

    try:
        # Some script files seem to be incompatible with utf-8
        # We let open() replace problem characters, since we only count lines.
        _astroid_node = astroid.parse(_file_string)
        _file_string = None
    except astroid.exceptions.AstroidSyntaxError:
        _file_string = None
        return None

    _multiline_comments = _get_docstring_lines(
        _get_docstrings(_astroid_node)
    )

    # tokenize, used to identify # comments,
    # only uses objects with readline function.
    # This means we cannot reuse the string already read.
    _single_comments = _get_single_comments(_file_path)

    _commented_lines_of_code = _single_comments + _multiline_comments

    if _lines_of_code:
        return _commented_lines_of_code / _lines_of_code
    return None

def _get_single_comments(_file_path):
    """ Uses tokenize to identify # comments and counts their occurrences. """
    try:
        _file = open(_file_path, 'r', errors='replace')
    except FileNotFoundError:
        return None

    _single_comments = [
        token
        for _token_type, token, _, _, _
        in tokenize.generate_tokens(_file.readline)
        if _token_type == tokenize.COMMENT
    ]
    _file.close()
    _comment_count = len(_single_comments)
    _single_comments = None
    return _comment_count

def _get_docstring_lines(docstring_list: list) -> int:
    """ Counts non empty lines in a list of docstrings. """

    # When we did not find any docstrings, the docstring lines are 0.
    if not docstring_list:
        return 0

    _disassembled_docstrings = []

    for _string in docstring_list:
        try:
            _disassembled_docstrings = _disassembled_docstrings + re.split(r'\s*\n\s*', _string)
        except:
            print(docstring_list)
            raise ValueError

    # Splitting might have created empty strings.
    # We do not want to count those.
    _docstring_non_blank_lines = [_line for _line in _disassembled_docstrings if _line]

    return len(_docstring_non_blank_lines)


def _get_docstrings(astroid_node: astroid.node_classes) -> list:
    """ Go through an astroid tree and get all docstrings.

    We use recursive traversal of the astroid parse tree.
    This seemed to be shorter and more intuitive than loops.
    """
    # This should happen at the leave nodes of the tree,
    # ending the recursion.
    if not astroid_node.bool_value():
        return []
    _list = []

    # Getting the docstring of the current node and
    # all its children recursively will give us all
    # docstrings of the current subtree.
    if hasattr(astroid_node, 'doc'):
        _list.append(astroid_node.doc)

    for astroid_child in astroid_node.get_children():
        _list = _list + _get_docstrings(astroid_child)
    return [_string for _string in _list if _string]
