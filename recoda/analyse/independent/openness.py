""" All metrics functions measuring the understandability subfactor. """

import re
from subprocess import Popen, PIPE


def license_type(project_path: str) -> str:
    """ Get the license of a project is licensed under if it is an open license. """
    _process = Popen(["licensee", "detect", project_path], stdout=PIPE)
    _output = _process.communicate()[0].decode("utf-8")
    _output_lines = _output.split('\n')

    for _line in _output_lines:
        _license = re.match(r'License:\s*(.+)', _line)
        if _license:
            if _license.group(1) == "None":
                return None
            return _license.group(1)

    return None
