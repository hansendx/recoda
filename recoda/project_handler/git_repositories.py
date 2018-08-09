""" The git_projects module offers discovery and handling functionality for git repositories.

The module searches recursively through a directory tree and discovers all git repositories.
Identified repositories can be iterated over and interacted with.
Interaction with the repositories, is limited to the functionality needed to analyse the
research software projects contained inside.
"""

import os
import glob

import git

class repository_handler(object):
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

        self._repository_list = get_repository_list(base_folder=base_folder)

        self._repository_dict = {}

        for repo in self._repository_list:
            self._repository_dict[repo.working_dir] = repo



    def get_repository_dict(self) -> dict:
        """ Return the instance variable containing all repositories and their paths.
        
        :returns: A dict with paths as keys.
                  Values are the git.Repo objects
                  of the repositories located at the path.
        """
        return self._repository_dict





    def get_repository_list(self) -> list:
        """ Return the instance variable containing all repositories.
        
        :returns: A list of git.Repo objects.
        """
        return self._repository_list



def get_repository_list(base_folder: str) -> list:
    """ Return a list of all git repositories in a directory subtree.

    :param base_folder: Folder, that should be recursively searched through,
                        to find all git repositories.
    :returns:           List of git.Repo objects. Determined by searching
                        through a directory tree for git repositories.
    """
    _dot_git_folder = glob.glob('%s/%s' % (base_folder, '**/.git') )
    _git_folders =  [os.path.dirname(path) for path in _dot_git_folder]
    _repositories = [git.Repo.init(folder) for folder in _git_folders]

    return _repositories