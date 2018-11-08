""" Offers functionality for command line calls.

An approach, using multiprocessing became necessary because runs started to become very long
when introducing the average comment density measure.

Multiprocessing did however take more and more ram without freeing it.
For this reason several lines to free up space 'manually' where added.
Files are closed explicitly after use, string values are set to None.
The dataframe used to gather all metrics is also periodically written to
a csv file and its content so far is then deleted.
"""

import argparse
import os
from multiprocessing import Pool

import pandas

import recoda.analyse.python.metrics
import recoda.analyse.r.metrics
import recoda.project_handler.git


def parse_arguments() -> argparse.Namespace:
    """ Reads command line arguments.
    :returns: Values of accepted command line arguments.
    """
    _parser = argparse.ArgumentParser(
        description="""Measures quality attributes of software projects."""
    )
    _parser.add_argument(
        '-l',
        '--language',
        type=str,
        help="The Programming language of the Projects.",
        required=True,
        choices=['python', 'r'],
    )
    _parser.add_argument(
        '-b',
        '--base-dir',
        type=str,
        help="Base path to search projects.",
        required=True
    )
    _parser.add_argument(
        '-t', '--project-type', type=str,
        help=(
            "Type of the projects to be analyzed. "
            "The project handler will only look for git repositories in the base directory, "
            "and ignore anything else. "
            "directory will cause the handler to treat every folder in the base dir as project. "
        ),
        required=False,
        choices=['git', 'directory'],
        default='directory'
    )
    _parser.add_argument(
        '-f',
        '--file-output',
        type=str,
        help=(
            "Full Path to a file in wich the results are going to be written. "
            "Existing files will be overwritten. "
        ),
        required=False
    )
    _parser.add_argument(
        '-p',
        '--processes',
        type=int,
        help=(
            "Maximum number of processes run in parallel. "
            "Number of actual processes run might be less, "
            "if the system does not have the ressources."
        ),
        choices=range(1, 200),
        metavar='1 to 200',
        default=5
    )
    return _parser.parse_args()

class MeasureProjects():
    """ Goes through all projects and returns their measurements in a DataFrame

    :returns:   A pandas dataframe with all Projects accessible through the handler
                and a column for every metric measured.
    """


    # We want to dispatch functions from different packages,
    # depending on the language of scripts, that is supposed to be
    # measured. For now the easiest way was to split the dispatcher
    # dict into one for the functions and one for the packages
    # containing language specific functions.
    _METRICS_DISPATCHER = {
        #'packageability': "packageability",
        'flesch_reading_ease': "flesch_reading_ease",
        'project_readme_size': "project_readme_size",
        'flesch_kincaid_grade': "flesch_kincaid_grade",
        'average_comment_density': "average_comment_density",
        'average_standard_compliance': "average_standard_compliance",
        'license_type': "license_type",
        'testlibrary_usage': "testlibrary_usage"
    }

    _LANGUAGE_DISPATCHER = {
        'python': recoda.analyse.python.metrics,
        'r': recoda.analyse.r.metrics
    }

    def __init__(
            self,
            project_measure_handler,
            language: str,
            multiprocessing_chunk_size: int = 5
        ):
        self.project_handler = project_measure_handler
        self.metrics = self._LANGUAGE_DISPATCHER[language]
        self._multiprocessing_chunk_size = multiprocessing_chunk_size

        # We set ids "measure function" to string, so we can
        # send all fields through the function dispatcher.
        # This will just give back us back the id for the id field.
        self._metrics_dispatcher = {'id': str}

        # We build and gather all functions in a dispatcher list
        # to measure them in the measure method.
        for _metric, _function in self._METRICS_DISPATCHER.items():
            try:
                self._metrics_dispatcher[_metric] = getattr(
                    self.metrics,
                    _function
                    )
            except AttributeError:
                #TODO LOG that the language lacks the requested metric.
                pass

        _column_list = [column for column in self._metrics_dispatcher]
        self._dataframe = pandas.DataFrame(columns=_column_list)


    def measure(self) -> pandas.DataFrame:
        """ Go through all Projects in the instances handler and measure them.

        Does not go through the measurement process if already called once.

        :returns: The results from a previous run of the method or,
                  if no previous results exist, the results calculated
                  during this run.
        """

        if not self._dataframe.empty:
            return self._dataframe

        # Save all project directories in a list to count them and
        # print a value for total projects.
        _directories = [_dir for _dir in self.project_handler.get_project_directories()]
        _projects = len(_directories)

        _measurement_chunk = []
        for _projects_measured, _current_project_directory in enumerate(_directories):
            # TODO read existing file, get already measured projects and skip them.

            # TODO set up logger
            print(_current_project_directory+':', _projects_measured+1, 'from', _projects, sep=' ')
            # A chunk element not only consist of the path to the project
            # but also the metrics dispatcher dict.
            # Multiprocessing does not function, when called from here directly.
            # This means we need to call it from a function where the dispatcher is not in scope.
            # This in turn means we have to pass the dispatcher dict along with the path.
            _measurement_chunk.append(
                (
                    _current_project_directory,
                    self._metrics_dispatcher
                )
            )
            # The chunk is filled to its max value so we send it to the multiprocessing function.
            if (_projects_measured + 1) % self._multiprocessing_chunk_size == 0:
                _rows = _run_multiprocessing(_measurement_chunk)

                # Free up memory
                _measurement_chunk = []
                # _run_multiprocessing gave us a list with a list item for every project,
                # we need to ingest every item into the dataframe.
                for _row in _rows:
                    self._dataframe = self._dataframe.append(_row, ignore_index=True)
                yield self._dataframe
                # We remove the dataframes content to save memory
                self._dataframe = self._dataframe.iloc[0:0]

        # If we did not have enough projects left for a
        # full sized chunk, we will cover the rest here.
        _rows = _run_multiprocessing(_measurement_chunk)
        _measurement_chunk = []
        for _row in _rows:
            self._dataframe = self._dataframe.append(_row, ignore_index=True)
        yield self._dataframe

def _measure(_project_directory: str, _metrics_dispatcher: dict) -> dict:
    """ Iterate over all metrics for one project.

    :param _project_directory:  The path to a projects base directory.
    :param _metrics_dispatcher: Dictionary the measurement names as keys and
                                the measure functions as values.
    """
    _project_measures = {}
    for _column, _function in _metrics_dispatcher.items():
        _project_measures[_column] = _function(_project_directory)
    return _project_measures

def _run_multiprocessing(_chunk: list) -> list:
    """ Run project measurements in parallel.

    This needs to be outside the object, calling it.
    multiprocessing otherwise complains about not being able
    to pickle.
    This also created the need to pass the the dispatcher to the
    non member functions, to iterate over it.
    Using starmap enables us to pass two arguments, path and
    dispatcher dictionary, to the function handled
    by multiprocessing.

    :param _chunk: A list of tuples. The first element
                   is the path to a project. The second
                   a dictionary with measurement functions
                   that are supposed to be executed with the path.
    """
    _measure_pool = Pool()
    _rows_of_project_measures = _measure_pool.starmap(
        _measure,
        _chunk
    )
    _measure_pool.close()
    return _rows_of_project_measures


def _main():
    """ Main function for executing from the command line. """
    _arguments = parse_arguments()

    # Git is currently the only project handler type.
    if _arguments.project_type == 'git':
        _handler = recoda.project_handler.git.Handler(_arguments.base_dir)
    else:
        raise ValueError('Project type not supported.')


    _measurement_object = MeasureProjects(
        project_measure_handler=_handler,
        language=_arguments.language,
        multiprocessing_chunk_size=_arguments.processes
        )
    _measurement_generator = _measurement_object.measure()

    # We want to print a header, if we create a new file.
    if not os.path.isfile(_arguments.file_output):
        _dataframe = next(_measurement_generator)
        _dataframe.to_csv(path_or_buf=_arguments.file_output)

    for _dataframe in _measurement_generator:
        with open(_arguments.file_output, 'a') as fileout:
            _dataframe.to_csv(fileout, header=False)



if __name__ == '__main__':
    _main()
