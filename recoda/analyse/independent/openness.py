""" All metrics functions measuring the understandability subfactor. """

import re
import json
from subprocess import Popen, PIPE


def license_type(project_path: str) -> str:
    """ Get the license of a project is licensed under if it is an open license. """
    _process = Popen(
        [
            "licensee",
            "detect",
            "--confidence=60",
            "--json",
            project_path
        ],
        stdout=PIPE
    )
    _output = _process.communicate()[0].decode("utf-8")
    _output_dict = json.loads(_output)
    _license = _get_license(_output_dict)

    return _license

def _get_license(licensee_output: dict) -> str:
    """ Extract the license with most confidence. """

    _license = None
    _confidence = 0


    for _license_file in licensee_output['matched_files']:
        if _license_file['matched_license'] == 'NOASSERTION':
            if not _license:
                _license = 'unknown'
        elif _confidence < _license_file["matcher"]["confidence"]:
            _license = _license_file["matched_license"]
            _confidence = _license_file["matcher"]["confidence"]

    return _license
