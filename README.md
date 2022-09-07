# paperfetcher

[![PyPI version fury.io](https://badge.fury.io/py/paperfetcher.svg)](https://pypi.python.org/pypi/paperfetcher/)
[![Build Status](https://img.shields.io/endpoint.svg?url=https%3A%2F%2Factions-badge.atrox.dev%2Fpaperfetcher%2Fpaperfetcher%2Fbadge&style=flat)](https://actions-badge.atrox.dev/paperfetcher/paperfetcher/goto)
[![Website](https://img.shields.io/website?label=docs&url=https%3A%2F%2Fimg.shields.io%2Fwebsite%2Fhttps%2Fpaperfetcher.github.io%2Fpaperfetcher)](https://paperfetcher.github.io/paperfetcher)
[![GitHub license](https://badgen.net/github/license/paperfetcher/paperfetcher)](https://github.com/paperfetcher/paperfetcher/blob/master/LICENSE)
[![Open Issues](https://img.shields.io/github/issues-raw/paperfetcher/paperfetcher)](https://github.com/paperfetcher/paperfetcher/issues)

## About

Paperfetcher is a Python package to automate handsearching and citation searching
(snowballing) for systematic reviews. Paperfetcher works with Python 3.7+.

To learn more about Paperfetcher, visit [paperfetcher.github.io](https://paperfetcher.github.io/).

## Usage

To get started, browse the following *Getting Started* Jupyter notebooks (also in the `examples/` directory in this
repository):

1. [Getting started with handsearching](https://mybinder.org/v2/gh/paperfetcher/paperfetcher/master?labpath=examples%2F01_handsearching.ipynb)
2. [Getting started with citation searching](https://mybinder.org/v2/gh/paperfetcher/paperfetcher/master?labpath=examples%2F02_citation_searching.ipynb)

Once you understand the workflow, read the [Module Documentation](https://paperfetcher.github.io/paperfetcher/paperfetcher.html) to
learn more about paperfetcher's various modules, classes and functions.

## Installation

### Installation with pip

1. [Install pip](https://pip.pypa.io/en/stable/installation/)
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

## Running tests (if installed from source)

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

## The Team

Paperfetcher was developed by [Akash Pallath](https://apallath.github.io) at the [University of Pennsylvania](https://www.upenn.edu) and [Qiyang Zhang](https://qiyangzh.github.io) at the [Johns Hopkins University](https://www.jhu.edu).
