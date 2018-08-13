""" The git_projects module offers discovery and handling functionality for git repositories.

The module searches recursively through a directory tree and discovers all git repositories.
Identified repositories can be iterated over and interacted with.
Interaction with the repositories, is limited to the functionality needed to analyse the
research software projects contained inside.
"""

from copy import deepcopy
import os
import glob

import git

class Handler(object):
    """ Keep a list of git repositories and offer functions to analyse them."""
    
    
    def __init__(self, base_folder: str):
        """ Initialise repository_handler.

        :ivar _repository_list:     A list filled with git.Repo objects.
                                    Created from the git repositories found
                                    in the base_folder.
        :ivar _repository_dict:     A dictionary with the git.Repo objects
                                    in _repository_list as values and the path
                                    to the directory of the repo as corresponding key.

        :param base_folder:         The root folder supposed to contain all 
                                    git repositories to work with.
        """

        self._base_folder = base_folder

        self._project_dict = self._create_project_dict()

    def get_project_directories(self) -> str:
        """ Generator to output project directories.
        
        :returns: Generator to iterate over project directories.
        """
        for _project in self._project_dict:
            yield _project
    
    def get_project_objects(self) -> git.repo.base.Repo:
        """ Generator to output project Repo objects.
        
        :returns: Generator to iterate over project Repo objects.
        """
        for _project in self._project_dict:
            yield self._project_dict[_project]['project']

    def get_identifier(self, project: git.repo.base.Repo) -> str:
        """ Return an identifier for a repository. """
        return self._project_dict[project.working_dir]['id']

    def get_project_dict(self) -> dict:
        """ Return the instance variable containing all repositories and their paths.
        
        :returns: A dict with paths as keys.
                  Values are the git.Repo objects
                  of the repositories located at the path.
        """
        return deepcopy(self._project_dict)

    @staticmethod
    def _create_identifier(_repo: git.repo.base.Repo) -> str:
        """ builds an identifier string for a repo. """
        if hasattr(_repo.remotes, 'origin'):
            return _repo.remotes.origin.url
        return _repo.working_dir

    def _create_project_dict(self) -> dict:
        """ Return a dictionary of all git repositories in a directory subtree.

        :returns:           Dictionary with the project location as keys,
                            and dictionary as value. The nested 
                            Dictionary contains the project as
                            git.repo.base.Repo object and an id.
        """

        _dot_git_folder = glob.glob('%s/%s' % (self._base_folder, '**/.git'))
        _git_folders =  [os.path.dirname(path) for path in _dot_git_folder]
        _repositories = [git.Repo.init(folder) for folder in _git_folders]

        _projects = {}
        for _repo in _repositories:
            _projects[_repo.working_dir] = {
                'project': _repo,
                'id': self._create_identifier(_repo)
            }
        return _projects

