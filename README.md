<p align="center">
    <img alt="Logo" src=https://github.com/its-hmny/ChimeraScript/blob/doc/readme/assets/ChimeraScript.png?raw=true">
</p>

<p align="center">
    <img alt="GPLv3 License" src="https://img.shields.io/badge/License-GPL%20v3-yellow.svg">
    <img alt="Code Size" src="https://img.shields.io/github/languages/code-size/its-hmny/ChimeraScript?color=green&label=Code%20Size">
    <img alt="Release" src="https://img.shields.io/github/v/release/its-hmny/ChimeraScript?label=Version">
</p>

# ChimeraScript

## A suit of Python scripts for my everyday usage

This project contains a list of simple but useful Python scripts.
Most of them are used to automate boring or repetitive tasks (e.g. backup to a remote location).

The majority the script available in this repository are born from my necessities but the hope for the future of the project is to become a go-to spot to find quick and easy automation solution to everyday problems.

## Installation

While a `requirements.txt` is provided in the project and can be used to install all the needed dependencies, is advised to use [Poetry](https://python-poetry.org/) instead to manage the project dependencies since its better functionalities and its more complete with respect to [pip](https://pip.pypa.io/en/stable/).

To install and run a script with pip, simply type in your terminal

```bash
  pip3 install -r requirements.txt
  python3 scripts/GitPuller.py ...
```

To install the dependencies and run the scripts with poetry, use:

```bash
  poetry install
  poetry run python3 scripts/GitPuller.py ...
```

<!--
    TODO add it later
    ## Demo
    Insert gif or link to demo
-->

## Running Tests

Each scripts has its own test suite in the `tests` folder, the test are run with [pytest](https://docs.pytest.org/en/7.1.x/).

To run the full test suite of every script simply type:

```bash
  poetry run pytest
```

while to run one or more specific test suites, specify the one desired as in the example:

```bash
  poetry run pytest tests/test_gitpuller.py
```

## Acknowledgements

- [Poetry](https://python-poetry.org/)
- [Pytest](https://docs.pytest.org/en/7.1.x/)
- [Pytube](https://pytube.io/en/latest/)
- [Rich](https://rich.readthedocs.io/en/stable/)
- [readme.so](https://readme.so/)

## Authors

- [@its-hmny](https://www.github.com/its-hmny) Follow me on [Twitter](https://twitter.com/its_hmny) as well

## License

This project is distributed under the [GPLv3](https://choosealicense.com/licenses/gpl-3.0/) license.
