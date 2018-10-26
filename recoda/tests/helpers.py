
import os
import random
import re
import string
from shutil import rmtree
from urllib.parse import urlparse

from git import Repo


def remove_test_repositories(base_folder: str):
    """ Remove all files from all subdirectories and then the base folder and its empty children. """

    # The test_base_folder should not already exist.
    if os.path.exists(base_folder):
        rmtree(base_folder)

def create_test_repositories(repo_base_folder, real_repo_url: str=''):

    # Make sure the test area is clean.
    remove_test_repositories(base_folder=repo_base_folder)

    os.makedirs(repo_base_folder)

    repositories = []

    if real_repo_url:
        _name = urlparse(real_repo_url).path
        _name = re.sub(r'^\/', '', _name)
        _name = re.sub(r'\.git$', '', _name)
        _name = re.sub(r'\/', '__', _name)
        _repo = Repo.clone_from(
            real_repo_url,
            "{}/{}".format(repo_base_folder, _name)
        )
        repositories.append(_repo)


    # Generate some random repositories.
    for _repository_index in range(0, random.randint(4, 6)):
        _folder_name = '%s/%s' % (
            repo_base_folder,
            ''.join(
                random.choices(
                    string.ascii_uppercase + string.digits, k=10
                )
            )
        )

        _repository = Repo.init(_folder_name)

        repositories.append(_repository)

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

    return repositories
