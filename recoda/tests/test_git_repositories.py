""" Unit-test module for the testing of the git_repositories module.

"""

import os
import random
import string
import unittest
from shutil import rmtree

from git import Repo

from recoda.project_handler import git_repositories


class TestRepositoryHandler(unittest.TestCase):
    """ Test the module function to find git repositories in a subtree. """

    @staticmethod
    def remove_test_repositories(base_folder: str):
        """ Remove all files from all subdirectories and then the base folder and its empty children. """

        # The test_base_folder should not already exist.
        if os.path.exists(base_folder):
            rmtree(base_folder)
            return

    def setUp(self):
        self.repo_base_folder = os.path.abspath('./test_repo_base')

        # Make sure the test area is clean.
        self.remove_test_repositories(base_folder=self.repo_base_folder)

        os.makedirs(self.repo_base_folder)

        self.repositories = []


        # Generate some random repositories.
        for _repository_index in range(0, random.randint(4, 6)):
            _folder_name = '%s/%s' % (
                self.repo_base_folder,
                ''.join(
                    random.choices(
                        string.ascii_uppercase + string.digits, k=10
                    )
                )
            )

            _repository = Repo.init(_folder_name)

            self.repositories.append(_repository)

            # Generate some randomly named files, add and commit them. 
            for _file_number in range(1, random.randint(2, 10)):
                _file_name = '%s/%s' % (
                    _folder_name,
                    ''.join(
                        random.choices(
                            string.ascii_uppercase + string.digits, k=10
                        )
                    )
                )
                # Create file filled with a random string.
                with open(_file_name, 'w') as _file:
                    _file.write(
                        ''.join(
                            random.choices(
                                string.ascii_uppercase + string.digits, k=random.randint(10, 100)
                            )
                        )
                    )
                # Add and commit file.
                _repository.index.add([_file_name])
                _repository.index.commit('commit number %s' % _file_number)

    def test_get_repository_list(self):
        """ Test the function, returning a list of all git repositories in a directory subtree."""
        _expected_list = self.repositories
        _test_list = git_repositories.get_repository_list(base_folder=self.repo_base_folder)

        self.assertEqual(len(_expected_list), len(_test_list))

        for repo in _expected_list:
            self.assertIn(repo, _test_list)

    def test_repository_handler(self):
        """ Test the repository handler object. """

        _test_object = git_repositories.repository_handler(
            base_folder=self.repo_base_folder
        )

        _test_list = _test_object.get_repository_list()
        _expected_list = self.repositories
    
        # Test the correctness of the repository list.
        self.assertEqual(len(_expected_list), len(_test_list))

        for repo in _expected_list:
            self.assertIn(repo, _test_list)
        _test_list = None

        _test_dict = _test_object.get_repository_dict()

        self.assertEqual(len(_test_dict), len(_expected_list))

        for repo in _expected_list:
            self.assertIn(repo.working_dir, _test_dict)
            self.assertEqual(repo, _test_dict[repo.working_dir])



    def tearDown(self):
        """ Remove the created test git repositories. """
        self.remove_test_repositories(self.repo_base_folder)


