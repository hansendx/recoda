""" Provides functionality to calculate software metrics in python projects.
"""

from recoda.analyse.python import (
    _installability
)

# pylint: disable-msg=c0103
# For now this seems to be the most streamline method of decentralization
# of this module. We want to call all functions via the metrics but we do
# not want it to be too long and unreadable. Wrapping the private module
# functions into a barebones would just lead to a lot more unnecessary code.

packageability = _installability.packageability
