""" Test the helper functions of the recoda.analyse package. """

import argparse
import logging
import os
import sys
import shutil
import tempfile
import unittest

from recoda.analyse.helpers import (
    search_filename
)

class TestSearchFilename(unittest.TestCase):

    def setUp(self):
        """ Create a mock base folder with files to test. """
        _base_folder = tempfile.mkdtemp()
        _folder = "package_dir"
        _file_name = "setup.py"
        _file_glob = "*" + _file_name[2:]
        # Where the files will be.
        _files = [
            "{base}/{folder}/{file}".format(
            base=_base_folder,
            folder=_folder,
            file=_file_name
            ),
            "{base}/{file}".format(
            base=_base_folder,
            file=_file_name
            )
        ]
        # create subfolder
        os.makedirs("{base}/{folder}".format(
            base=_base_folder,
            folder=_folder
            )
        )
        

        # Creating the files we want to find.
        for file in _files:
            open(file, 'w').close()

        self._file_name = _file_name
        self._file_glob = _file_glob
        self._files = _files
        self._base_folder = _base_folder

    def test_search_filename(self):
        """ Do we find all files we created matching a filename or glob? """

        # Test normal file name
        _file_test_result = search_filename(
            base_folder=self._base_folder,
            file_name=self._file_name
        )
        # We can't test for equality directly since we do not know
        # the ordering of the resulting list.
        for _file in _file_test_result:
            self.assertIn(
                _file,
                self._files
            )
        self.assertEqual(
            len(_file_test_result),
            len(self._files)
        )

        # Test file glob
        _glob_test_result = search_filename(
            base_folder=self._base_folder,
            file_name=self._file_glob
        )
        # We can't test for equality directly since we do not know
        # the ordering of the resulting list.
        for _file in _glob_test_result:
            self.assertIn(
                _file,
                self._files
            )
        self.assertEqual(
            len(_glob_test_result),
            len(self._files)
        )

    def tearDown(self):
        """ Remove the mock base folder. """
        shutil.rmtree(self._base_folder)



