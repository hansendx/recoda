""" Provides functionality to calculate software metrics in python projects.
"""

from recoda.analyse.python import (
    _installability,
    _learnability,
    _understandability
)

# pylint: disable-msg=c0103
# For now this seems to be the most streamline method of decentralization
# of this module. We want to call all functions via the metrics but we do
# not want it to be too long and unreadable. Wrapping the private module
# functions into a barebones would just lead to a lot more unnecessary code.

# Installability related metrics.
packageability = _installability.packageability

# Learnability related metrics.

project_readme_size = _learnability.project_readme_size

flesch_reading_ease = _learnability.flesch_reading_ease

flesch_kincaid_grade = _learnability.flesch_kincaid_grade

# Understandability related metrics.

average_comment_density = _understandability.average_comment_density
