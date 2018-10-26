""" Module to share commonly used functionality in the analyse package. """

import glob

# To convert restructuredText to html
from docutils.core import publish_string

# To convert markdown to html
from markdown import markdown
# To extract text from html.
from bs4 import BeautifulSoup

def search_filename(
        base_folder: str,
        file_name: str,
        recursive_flag: bool = True
) -> dict:
    """ Return a list of paths to files searched and found.


    :param base_folder: The full path to the Folder, that should be searched through.
    :param file_name:   File name or glob of the item to search for.
    :returns:           A List with full pathes to files matching the file_name.
    """

    if recursive_flag:
        _recursive_glob = '{base}/**/{file}'.format(
            base=base_folder,
            file=file_name
        )

        _findings = glob.glob(_recursive_glob, recursive=recursive_flag)
    else:
        _glob = '{base}/{file}'.format(
            base=base_folder,
            file=file_name
        )
        _findings = glob.glob(_glob)


    return _findings

# The strip functions are indirectly testet by tests for learnability metrics.
def strip_text_from_html(html_content: str) -> str:
    """ Strips pure text from strings containing html. """
    _soup = BeautifulSoup(html_content, features="html.parser")
    _text = _soup.get_text(separator=" ")
    return _text

def strip_text_from_md(markdown_content: str) -> str:
    """ Strips pure text from strings containing Markdown. """
    _html_content = markdown(markdown_content)
    return strip_text_from_html(_html_content)

def strip_text_from_rst(rst_content: str) -> str:
    """ Strips pure text from strings containing RestructuredText. """
    _html_content = publish_string(rst_content, writer_name='html')
    return strip_text_from_html(_html_content)
