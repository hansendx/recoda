""" Unit-test module for the testing of the git project handler class.

"""

import tempfile
import unittest

from recoda.project_handler import git
from recoda.tests.helpers import (
    remove_test_repositories,
    create_test_repositories
)

EXISTING_REMOTE_REPO = 'https://github.com/hansendx/singularity_fsl_minimal.git'
EXISTING_REMOTE_REPO_ID = 'hansendx/singularity_fsl_minimal'


class TestRepositoryHandler(unittest.TestCase):
    """ Test the module function to find git repositories in a subtree. """

    def setUp(self):
        # Working in a tmp folder so we dont have juggle to much with paths
        # and dont risk cluttering the package directory.
        self.repo_base_folder = tempfile.mkdtemp()
        self.repositories = create_test_repositories(self.repo_base_folder, EXISTING_REMOTE_REPO)

        self.handler = git.Handler(base_folder=self.repo_base_folder)

    def test_get_repository_objects(self):
        """ Test the function, returning a list of all git repositories in a directory subtree."""
        _expected_list = self.repositories
        _test_list = [_object for _object in self.handler.get_project_objects()]

        self.assertEqual(len(_expected_list), len(_test_list))

        for repo in _expected_list:
            self.assertIn(repo, _test_list)

    def test_repository_handler(self):
        """ Test the repository handler object. """

        _test_object = git.Handler(
            base_folder=self.repo_base_folder
        )

        _test_list = [_object for _object in self.handler.get_project_objects()]
        _expected_list = self.repositories
    
        # Test the correctness of the repository list.
        self.assertEqual(len(_expected_list), len(_test_list))

        for repo in _expected_list:
            self.assertIn(repo, _test_list)
        _test_list = None

        _test_dict = _test_object.get_project_dict()

        self.assertEqual(len(_test_dict), len(_expected_list))

        for repo in _expected_list:
            self.assertIn(repo.working_dir, _test_dict)
            self.assertEqual(repo, _test_dict[repo.working_dir]['project'])

    def test_handler_get_identifier(self):
        """ Does the get_identifier create identifiers from repositories as expected? """
        _identifiers = [
            self.handler.get_identifier(_repo)
            for _repo in self.repositories
        ]
        # We want the git repo, that actually has a remote
        # url, to have an id constructed from that.
        self.assertIn(EXISTING_REMOTE_REPO, _identifiers)
        # We want all other projects to have an id based on their
        # folder location.
        for _repo in self.repositories:
            _id = self.handler.get_identifier(_repo)
            if EXISTING_REMOTE_REPO != _id:
                self.assertEqual(_id, _repo.working_dir)

                

    def tearDown(self):
        """ Remove the created test git repositories. """
        remove_test_repositories(self.repo_base_folder)


