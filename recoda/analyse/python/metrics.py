""" Provides functionality to calculate software metrics in python projects.
"""

from recoda.analyse.python import (
    _installability
)

# pylint: disable-msg=c0103

packageability = _installability.packageability
