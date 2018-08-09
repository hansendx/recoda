""" Setup script for the SingularityAutobuild Package."""
from setuptools import setup, find_packages
import glob

setup(
    name='ReCodA',
    version='0.1.0',
    author='Dominique Hansen',
    author_email='Dominique.Hansen@hu-berlin.de',
    packages=[
        'recoda',
        'recoda.analyse',
        'recoda.project_handler',
        'recoda.tests'
    ],
    license='3-clause BSD',
    url='https://scm.cms.hu-berlin.de/hansendx/ReCodA',
    description=(
        'Statically analyse a collection of software projects.'
        'Analysis is based on a quality model focused on research software.'
    ),
    long_description=open('README.rst').read(),
    install_requires=[
        # Needed to work with the repositories containing the software projects.
        "GitPython"
    ],
    keywords= 'science research engineering static analysis',
    classifiers = [
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6'
    ],
    zip_safe=True
)