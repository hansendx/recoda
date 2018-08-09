""" Offers functionality for command line calls. """

import argparse

def parse_arguments() -> argparse.Namespace:
    """ Reads command line arguments.
    :returns: Values of accepted command line arguments.
    """
    _parser = argparse.ArgumentParser(
        description="""
        """
    #TODO Add a description
    )
    _parser.add_argument('-b', '--base-dir', type=str, help="Base path to search projects.", required=True)
    _parser.add_argument(
        '-t', '--project-type', type=str,
        help="""Type of the projects to be analyzed.
        The project handler will only look for git repositories in the base directory,
        and ignore anything else.
        directory will cause the handler to treat every folder in the base dir as project.""",
        required=False,
        choices=['git', 'directory'],
        default='directory')
    return _parser.parse_args()

