""" Setup script for the SingularityAutobuild Package."""
from setuptools import setup, find_namespace_packages

setup(
    name='ReCodA',
    version='0.1.0',
    author='Dominique Hansen',
    author_email='Dominique.Hansen@hu-berlin.de',
    packages=find_namespace_packages(),
    package_data={
        'recoda.tests': ['data/mock_setup_py/*', 'data/mock_docs/*']
    },
    license='MIT License',
    url='https://scm.cms.hu-berlin.de/hansendx/ReCodA',
    description=(
        'Statically analyse a collection of software projects.'
        'Analysis is based on a quality model focused on research software.'
    ),
    long_description=open('README.rst').read(),
    install_requires=[
        # Needed to work with the repositories.
        "GitPython==2.0.4",
        # For handling the measurement data.
        "pandas==0.23.4",
        # For measuring the packageability.
        "pyroma==2.4",
        # Calculates readability metrics.
        "textstat==0.4.1",
        # To strip markup from Documentation files.
        "beautifulsoup4==4.6.3",
        "Markdown==2.6.11",
        # To measure code related metrics.
        "astroid==2.0.4",
        # Test for compliance and errors.
        "pycodestyle==2.3.1",
        "pyflakes==1.6.0", 
        # Get requirements from imports
        "pipreqs==0.4.9",
        # Type hints
        "typing >= 3.6.6"
    ],
    keywords='science research engineering static analysis',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License'
    ],
    zip_safe=True
)
