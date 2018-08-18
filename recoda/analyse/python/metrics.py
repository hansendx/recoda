""" Provides functionality to calculate software metrics in python projects.
"""

import os
from recoda.analyse.python import (
    _installability
)

packageability = _installability.packageability