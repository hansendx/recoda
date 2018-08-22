""" Offers functionality for command line calls. """

from typing import Union

import argparse
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
        help="""Type of the projects to be analyzed.
        The project handler will only look for git repositories in the base directory,
        and ignore anything else.
        directory will cause the handler to treat every folder in the base dir as project.""",
        required=False,
        choices=['git', 'directory'],
        default='directory'
    )
    _parser.add_argument(
        '-f',
        '--file-output',
        type=str,
        help="""Full Path to a file in wich the results are going to be written.
        Existing files will be overwritten.""",
        required=False
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
        'packageable': "packageable"
    }

    _LANGUAGE_DISPATCHER = {
        'python': recoda.analyse.python.metrics,
        'r': recoda.analyse.r.metrics
    }

    def __init__(
            self,
            project_measure_handler: Union[recoda.project_handler.git],
            language: str
        ):
        self.project_handler = project_measure_handler
        self.metrics = self._LANGUAGE_DISPATCHER[language]

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

        for _project_directory in self.project_handler.get_project_directories():
            _row = {}
            for _column, _function in self._metrics_dispatcher.items():
                _row[_column] = _function(_project_directory)

            self._dataframe = self._dataframe.append(_row, ignore_index=True)

        return self._dataframe


if __name__ == '__main__':
    _arguments = parse_arguments()
    if _arguments.project_type == 'git':
        _handler = recoda.project_handler.git.Handler(_arguments.base_dir)

    _measurements = MeasureProjects(_handler, _arguments.language)
    _dataframe = pandas.DataFrame()
    _dataframe = _measurements.measure()
    _dataframe.to_csv(path_or_buf=_arguments.file_output)
