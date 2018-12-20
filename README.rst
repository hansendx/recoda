ReCodA (Research Code Analysis)
===============================

This project aims to evaluate research
software projects for scientific analysis.
It measures the software projects
based on criteria, focused on researchers needs.

Faulty code or code that is not
understood correctly can lead to problems in the reproducibility
of results, the validity of results
obtained using it and can promote software abandonment
and constant rewriting of software.

Installation
------------

ReCodA depends on a ruby gem `licensee <https://github.com/benbalter/licensee>`_
to run properly.
All other dependencies are in the requirements.txt and setup.py.
The setup.py needs setuptools to function.
It can either be installed as requirement with:

.. code-block:: bash

    pip install -r requirements.txt

Or It can be installed manually:

.. code-block:: bash

    pip install setuptools



The package can be installed via pip
from the directory the setup.py resides in.

.. code-block:: bash

    pip install .


Functionality
-------------

The installation with pip creates an entrypoint
in the form of the command "recoda".

For help with the command line interface use:

.. code-block::

    recoda -h

Or if it was installed in a virtual environment:

.. code-block::

    python -m recoda -h

The code itself is documented with docstrings and a
`Sphinx <http://www.sphinx-doc.org/en/master/>`_
automated documentation is in the works.

Modules related to measures are in recoda/analyse.
Tests and related data are in recoda/tests.
