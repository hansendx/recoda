""" Test the module that measures software projects. """

import os
import unittest
import tempfile

from recoda.analyse.python.metrics import (
    packageability
)


class TestPackageable(unittest.TestCase):


    #TODO Create test data dir and move the mock setup.py files there.
    # Hard coded the content here to save time for now.
    _SCORED_EIGHT_SETUP = """
from setuptools import setup, find_packages
import glob

setup(
    name='ReCodA',
    version='0.1.0',
    author='Dominique Hansen',
    author_email='Dominique.Hansen@hu-berlin.de',
    packages=[
        'recoda',
        'recoda.analyse',
        'recoda.project_handler',
        'recoda.tests'
    ],
    license='3-clause BSD',
    url='https://scm.cms.hu-berlin.de/hansendx/ReCodA',
    description=(
        'Statically analyse a collection of software projects.'
        'Analysis is based on a quality model focused on research software.'
    ),
    long_description="I am to short.",
    install_requires=[
        # Needed to work with the repositories containing the software projects.
        "GitPython"
    ],
    keywords= 'science research engineering static analysis',
    classifiers = [
        'Programming Language :: Python :: 3'
    ]
)
   """

    _SCORED_TEN_SETUP = """from setuptools import setup, find_packages
import glob

setup(
    name='ReCodA',
    version='0.1.0',
    author='Dominique Hansen',
    author_email='Dominique.Hansen@hu-berlin.de',
    packages=[
        'recoda',
        'recoda.analyse',
        'recoda.project_handler',
        'recoda.tests'
    ],
    license='3-clause BSD',
    url='https://scm.cms.hu-berlin.de/hansendx/ReCodA',
    description=(
        'Statically analyse a collection of software projects.'
        'Analysis is based on a quality model focused on research software.'
    ),
    long_description=" Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut accumsan et justo quis vehicula. Donec sit amet leo tincidunt diam blandit volutpat. Integer semper nunc quam, vel semper nunc congue non. Nulla ultricies fermentum neque et elementum. Proin id risus sed nunc ornare pellentesque vitae maximus magna. Cras vehicula ac tellus ac finibus. Fusce ornare dui sit amet libero rutrum, at accumsan erat facilisis. Proin fermentum ante risus, vitae vestibulum mauris tempor non. Donec ultrices sapien non felis elementum venenatis. Mauris id augue id justo imperdiet tempor vel in ex. Duis suscipit dapibus sapien, elementum cursus justo facilisis nec. Etiam tempus odio eu quam sollicitudin, faucibus tincidunt lorem porta. Fusce vitae convallis est. Sed malesuada viverra arcu id vulputate. Praesent porttitor urna non dui rhoncus pulvinar. Vivamus convallis nunc quis nunc volutpat efficitur. Phasellus accumsan vitae elit in posuere. Fusce tortor dui, porta a eleifend non, volutpat nec neque. Nam sollicitudin lacus magna, vitae aliquam ipsum dapibus rhoncus. Curabitur in tellus non leo volutpat congue eget eget diam. Maecenas elementum dictum dui, id hendrerit nunc sagittis sit amet. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Vestibulum ac auctor metus, non feugiat lacus. ",
    install_requires=[
        # Needed to work with the repositories containing the software projects.
        "GitPython"
    ],
    keywords= 'science research engineering static analysis',
    classifiers = [
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6'
    ],
    zip_safe=True
)
 """

    def setUp(self):
        """ Create two setup scripts to measure. """
        # TODO This should be possible to be more elegant.
        _base_folder = tempfile.mkdtemp()
        _scored_setup_dict = {}
        _scored_setup_dict[10] = "{base}/ten".format(
            base=_base_folder
        )
        _scored_setup_dict[8] = "{base}/eight".format(
            base=_base_folder
        )
        for _score, _folder in _scored_setup_dict.items():
            os.makedirs(_folder)
            if _score == 10:
                with open("{}/setup.py".format(_folder), "w") as _setup_file:
                    _setup_file.write(self._SCORED_TEN_SETUP)
            if _score == 8:
                with open("{}/setup.py".format(_folder), "w") as _setup_file:
                    _setup_file.write(self._SCORED_EIGHT_SETUP)
        self._scored_setup_dict = _scored_setup_dict

    def test_scoring(self):
        """ Compare the validated scores with packageable scores. """
        for _score, _folder in self._scored_setup_dict.items():
            _test_score = packageability(_folder)
            self.assertEqual(_score, _test_score)


