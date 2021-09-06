# paperfetcher

[![PyPI version fury.io](https://badge.fury.io/py/paperfetcher.svg)](https://pypi.python.org/pypi/paperfetcher/)
[![Build Status](https://img.shields.io/endpoint.svg?url=https%3A%2F%2Factions-badge.atrox.dev%2Fpaperfetcher%2Fpaperfetcher%2Fbadge&style=flat)](https://actions-badge.atrox.dev/paperfetcher/paperfetcher/goto)
[![Website](https://img.shields.io/website?label=docs&url=https%3A%2F%2Fimg.shields.io%2Fwebsite%2Fhttps%2Fpaperfetcher.github.io%2Fpaperfetcher)](https://paperfetcher.github.io/paperfetcher)
[![GitHub license](https://badgen.net/github/license/paperfetcher/paperfetcher)](https://github.com/paperfetcher/paperfetcher/blob/master/LICENSE)
[![Open Issues](https://img.shields.io/github/issues-raw/paperfetcher/paperfetcher)](https://github.com/paperfetcher/paperfetcher/issues)

## About

Paperfetcher is a Python package to mine papers for systematic reviews. In particular, paperfetcher automates the hand-search and snowball-search portions of the systematic review process.

Paperfetcher works with Python 3.7+.

## Usage

See the example Jupyter notebooks below to get started:

1. [Crossref hand-search getting started guide](https://nbviewer.jupyter.org/github/paperfetcher/paperfetcher/blob/master/examples/Crossref_hand_search.ipynb)
2. Crossref snowball-search getting started guide (coming soon!)

Once you understand the workflow, read the [Module Documentation](https://paperfetcher.github.io/paperfetcher/paperfetcher.html) to
learn more about how to use paperfetcher's various modules, classes and functions.

## Installation

### Installation with pip

1. [Install pip]
2. Install paperfetcher using pip:
```sh
pip install paperfetcher
```

### Installation from source

1. Clone this repository
2. In the repository directory, run
```sh
python setup.py install
```
or, if you have pip installed
```sh
pip install .
```

## Running tests (optional)

You can run tests to make sure that paperfetcher is working correctly on your system.

1. To run integration tests, in the repository directory, run
```sh
cd tests/tests_integration
pytest
```

2. To run unit tests, in the repository directory, run
```sh
cd tests/tests_unit
pytest
```
