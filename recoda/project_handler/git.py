""" The git_projects module offers discovery and handling functionality for git repositories.

The module searches recursively through a directory tree and discovers all git repositories.
Identified repositories can be iterated over and interacted with.
Interaction with the repositories, is limited to the functionality needed to analyse the
research software projects contained inside.
"""

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

        self._project_list = self._create_project_list()

        self._project_dict = self._create_project_dict()

    def get_identifier(self, project: git.repo.base.Repo) -> str:
        """ Return an identifier for a repository. """
        return self._project_dict[project.working_dir]['id']

    def get_project_dict(self) -> dict:
        """ Return the instance variable containing all repositories and their paths.
        
        :returns: A dict with paths as keys.
                  Values are the git.Repo objects
                  of the repositories located at the path.
        """
        return self._project_dict

    def get_project_list(self) -> list:
        """ Return the instance variable containing all projects.
        
        :returns: A list of git.Repo objects.
        """
        return self._project_list
        
    @staticmethod
    def _create_identifier(_repo: git.repo.base.Repo) -> str:
        """ builds an identifier string for a repo. """
        if hasattr(_repo.remotes, 'origin'):
            return _repo.remotes.origin.url
        return _repo.working_dir

    def _create_project_dict(self) -> dict:

        _dict = {}
        for _repo in self._project_list:
            _dict[_repo.working_dir] = {
                'project': _repo,
                'id': self._create_identifier(_repo)
            }
        return _dict

    def _create_project_list(self) -> list:
        """ Return a list of all git repositories in a directory subtree.

        :returns:           List of git.Repo objects. Determined by searching
                            through a directory tree for git repositories.
        """
        _dot_git_folder = glob.glob('%s/%s' % (self._base_folder, '**/.git'))
        _git_folders =  [os.path.dirname(path) for path in _dot_git_folder]
        _repositories = [git.Repo.init(folder) for folder in _git_folders]

        return _repositories
