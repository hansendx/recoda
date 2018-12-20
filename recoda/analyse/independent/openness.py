""" All metrics functions measuring the understandability subfactor. """

import json
from subprocess import Popen, PIPE

_APACHE_SNIPPET = 'the Apache License, Version 2.0'

def license_type(project_path: str) -> str:
    """ Gets projects license information.

    Call licensee and get the license that
    a project is licensed under.
    Licensee only recognizes a set of open source
    licenses, which also limits theoutput of this license.
    
    :param project_path: Path to the root folder of a project.
    :returns:            Name of the license with the highest
                         confidence value in the licensee output.
    """
    _process = Popen(
        [
            "licensee",
            "detect",
            # This is the default confidence value,
            # but its value is reiterated here
            # since it is somewhat hidden in the docs.
            "--confidence=98",
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
    """ Extract the license with most confidence.
    
    Parses licensee output for the license it is most
    confident in.

    :param licensee_output: Parsed json output from licensee
    :returns:               Name of the license with the highest
                            confidence value.
    """

    _license = None
    _confidence = 0


    for _license_file in licensee_output['matched_files']:
        if _license_file['matched_license'] == 'NOASSERTION':
            if not _license or _license == 'unknown':
                if _APACHE_SNIPPET in _license_file['content']:
                    # Apache 2.0 has a short version,
                    # that licensee does not seem to recognize.
                    # So we check if we can match the license snippet,
                    # if nothing else matches.
                    _license = 'Apache-2.0'
                else:
                    _license = 'unknown'
        elif _confidence < _license_file["matcher"]["confidence"]:
            _license = _license_file["matched_license"]
            _confidence = _license_file["matcher"]["confidence"]

    return _license
